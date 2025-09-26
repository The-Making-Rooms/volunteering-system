from django.http.request import HttpRequest
from django.http.response import HttpResponse
from typing import Optional
from django.shortcuts import render, get_object_or_404
from datetime import datetime
from django.contrib.auth.decorators import login_required
from commonui.views import check_if_hx
from opportunities.models import Opportunity
from django.db import connection
from typing import Iterable, Dict, Any, List, Tuple
from django.db.models import Exists, OuterRef, Min, Q, Exists, OuterRef, F, Value, BooleanField, Subquery, Count
from django.db.models import OuterRef, Subquery
from django.core.exceptions import PermissionDenied, ValidationError
from org_admin.models import OrganisationAdmin
from rota.models import VolunteerShift, Occurrence, OneOffDate, Role, Section, VolunteerOneOffDateAvailability, RSVPChoices
from opportunities.models import VolunteerRegistrationStatus

def triplets_to_shift_dicts(triplets: Iterable[Tuple[int, int, int | None]]) -> List[Dict[str, Any]]:
    """
    Convert (role_id, oneoffdate_id, section_id|None) triplets into
    dicts {'role': Role, 'schedule': OneOffDate, 'section': Section|None}
    with only three queries via in-bulk lookups.
    """
    role_ids: set[int] = set()
    ood_ids: set[int] = set()
    section_ids: set[int] = set()
    cached: List[Tuple[int, int, int | None]] = []

    for role_id, ood_id, section_id in triplets:
        cached.append((role_id, ood_id, section_id))
        role_ids.add(role_id)
        ood_ids.add(ood_id)
        if section_id is not None:
            section_ids.add(section_id)

    if not cached:
        return []

    role_map = Role.objects.in_bulk(role_ids)
    ood_map = OneOffDate.objects.in_bulk(ood_ids)
    section_map = Section.objects.in_bulk(section_ids) if section_ids else {}

    out: List[Dict[str, Any]] = []
    for role_id, ood_id, section_id in cached:
        out.append({
            'role': role_map.get(role_id),
            'schedule': ood_map.get(ood_id),            # schedule is the OneOffDate instance
            'section': section_map.get(section_id) if section_id is not None else None,
        })
    return out


def count_assigned_unconfirmed_active(one_off_date: OneOffDate, role: Role, section: Section | None) -> int:
    """
    Count unconfirmed VolunteerShifts for (OneOffDate, Role, [Section])
    whose Registration's latest VolunteerRegistrationStatus has registration_status.status == 'active'.
    """
    # Resolve occurrence id for the OneOffDate (unique relation)
    occ_id_sq = (
        Occurrence.objects
        .filter(one_off_date=one_off_date)
        .values('id')[:1]
    )  # [attached_file:1]

    base = VolunteerShift.objects.filter(
        occurrence_id=Subquery(occ_id_sq),
        role=role,
        section=section,
        confirmed=False,
    )  # [attached_file:1]

    # Subquery: latest VolunteerRegistrationStatus for this shift's registration
    # and select its registration_status.status directly
    latest_status_value_sq = (
        VolunteerRegistrationStatus.objects
        .filter(registration=OuterRef('registration'))
        .order_by('-date', '-id')            # latest first
        .values('registration_status__status')[:1]
    )  # [attached_file:4]

    qs = base.annotate(
        latest_status=Subquery(latest_status_value_sq)
    ).filter(
        latest_status='active'
    )  # [attached_file:4]

    return qs.count()



def count_available_volunteers_for_oneoff(one_off_date: OneOffDate, role: Role) -> int:
    """
    Count distinct registrations that:
      - declared availability for this OneOffDate,
      - have latest Registration status == 'active',
      - and do NOT have a clashing VolunteerShift at the same date/time.
    """
    # Overlap: any shift on same date overlapping [start_time, end_time]
    overlap_exists = Exists(
        VolunteerShift.objects.filter(
            registration=OuterRef('registration'),
            occurrence__date=one_off_date.date,
        ).filter(
            occurrence__start_time__lt=one_off_date.end_time,
            occurrence__end_time__gt=one_off_date.start_time,
        )
    )  # [attached_file:1]

    # Latest registration status value for this registration
    latest_status_value_sq = (
        VolunteerRegistrationStatus.objects
        .filter(registration=OuterRef('registration'))
        .order_by('-date', '-id')                      # latest first
        .values('registration_status__status')[:1]
    )  # [attached_file:4]

    qs = (
        VolunteerOneOffDateAvailability.objects
        .filter(one_off_date=one_off_date)
        .annotate(
            has_overlap=overlap_exists,
            latest_status=Subquery(latest_status_value_sq),
        )
        .filter(
            has_overlap=False,
            latest_status='active',
        )
        .values('registration')
        .distinct()
    )

    return qs.count()

def count_sent_and_accepted(one_off_date: OneOffDate, role: Role, section: Section | None):
    """
    Returns (sent_count, accepted_count) for the shift triple (OneOffDate, Role, [Section]),
    restricted to registrations whose latest VolunteerRegistrationStatus is 'active'.
    """
    # Resolve occurrence via subquery (unique relation to OneOffDate)
    from rota.models import Occurrence  # local import to avoid cycles  [attached_file:1]
    occ_id_sq = (
        Occurrence.objects
        .filter(one_off_date=one_off_date)
        .values('id')[:1]
    )  # [attached_file:1]

    # Base: confirmed shifts for this specific shift combo
    base_sent = VolunteerShift.objects.filter(
        occurrence_id=Subquery(occ_id_sq),
        role=role,
        section=section,
        confirmed=True,
    )  # [attached_file:1]

    # Latest registration status per registration (by date then id)
    latest_status_value_sq = (
        VolunteerRegistrationStatus.objects
        .filter(registration=OuterRef('registration'))
        .order_by('-date', '-id')
        .values('registration_status__status')[:1]
    )  # [attached_file:4]

    # Sent = confirmed AND latest status active
    sent_qs = base_sent.annotate(
        latest_status=Subquery(latest_status_value_sq)
    ).filter(
        latest_status='active'
    )  # [attached_file:4]

    sent_count = sent_qs.count()  # [attached_file:4]

    # Accepted = sent AND RSVP yes
    accepted_count = sent_qs.filter(
        rsvp_response=RSVPChoices.YES
    ).count()  # [attached_file:1]

    return accepted_count, sent_count

# Optional: constants matching the Opportunity.rota_config choices in the opportunities app
ROTA_CONFIG_SHARED = "SHARED"
ROTA_CONFIG_PER_ROLE = "PER_ROLE"

def iter_shift_triplets_for_opportunity(opportunity_id: int, oneoffdate_id: int | None = None, role_id: int | None = None):
    """
    Yields (role_id, oneoffdate_id, section_id|NULL) for the given opportunity,
    filtered optionally by oneoffdate_id and/or role_id.
    - SHARED: pairs each Role in the opportunity with OneOffDate where role_id IS NULL.
    - PER_ROLE: pairs each Role with OneOffDate where ood.role_id = role.id.
    Only returns OneOffDate rows with date >= CURRENT_DATE.
    Results are sorted by OneOffDate.date, then start_time.
    """
    with connection.cursor() as cur:
        # Fetch rota_config
        cur.execute("""
            select rota_config
            from opportunities_opportunity
            where id = %s
        """, [opportunity_id])  # [attached_file:1]
        row = cur.fetchone()
        if not row:
            return
        rota_config = row[0]

        # Build dynamic predicates
        extra_role_filter = ""
        extra_role_params = []
        if role_id is not None:
            extra_role_filter = " and r.id = %s"
            extra_role_params.append(role_id)

        extra_ood_filter = ""
        extra_ood_params = []
        if oneoffdate_id is not None:
            extra_ood_filter = " and ood.id = %s"
            extra_ood_params.append(oneoffdate_id)

        params = [opportunity_id] + extra_role_params + extra_ood_params

        if rota_config == ROTA_CONFIG_SHARED:
            # Situation A: shared dates (ood.role_id is null) within this opportunity
            sql = f"""
            with role_ood as (
                select r.id as role_id, ood.id as oneoffdate_id, ood.date, ood.start_time
                from rota_role r
                join rota_oneoffdate ood
                  on ood.opportunity_id = r.opportunity_id
                 and ood.role_id is null
                 and ood.date >= CURRENT_DATE
                where r.opportunity_id = %s
                {extra_role_filter}
                {extra_ood_filter}
            ),
            expanded as (
                -- explode sections if present
                select ro.role_id, ro.oneoffdate_id, s.id as section_id, ro.date, ro.start_time
                  from role_ood ro
                  join rota_section s on s.role_id = ro.role_id
                union all
                -- otherwise single row with null section
                select ro.role_id, ro.oneoffdate_id, null as section_id, ro.date, ro.start_time
                  from role_ood ro
                 where not exists (
                       select 1 from rota_section s2 where s2.role_id = ro.role_id
                 )
            )
            select role_id, oneoffdate_id, section_id
            from expanded
            order by date asc, start_time asc
            """
            cur.execute(sql, params)  # [attached_file:1]
        else:
            # Situation B: per-role dates (ood.role_id = r.id) within this opportunity
            sql = f"""
            with role_ood as (
                select r.id as role_id, ood.id as oneoffdate_id, ood.date, ood.start_time
                from rota_role r
                join rota_oneoffdate ood
                  on ood.role_id = r.id
                 and ood.date >= CURRENT_DATE
                where r.opportunity_id = %s
                {extra_role_filter}
                {extra_ood_filter}
            ),
            expanded as (
                select ro.role_id, ro.oneoffdate_id, s.id as section_id, ro.date, ro.start_time
                  from role_ood ro
                  join rota_section s on s.role_id = ro.role_id
                union all
                select ro.role_id, ro.oneoffdate_id, null as section_id, ro.date, ro.start_time
                  from role_ood ro
                 where not exists (
                       select 1 from rota_section s2 where s2.role_id = ro.role_id
                 )
            )
            select role_id, oneoffdate_id, section_id
            from expanded
            order by date asc, start_time asc
            """
            cur.execute(sql, params)  # [attached_file:1]

        for role_id_out, ood_id_out, section_id_out in cur.fetchall():
            yield role_id_out, ood_id_out, section_id_out  # [attached_file:1]


@login_required
def assign_rota(request: HttpRequest, opp_id: int, success: Optional[str] = None, error: Optional[str] = None) -> HttpResponse:


    #Get query parameters for filtering
    rget_role = request.GET.get("role")
    rget_date = request.GET.get("date")

    selected_role = rget_role if rget_role else None
    selected_date = rget_date if rget_date else None

    if request.method == "POST":
        post_role = request.POST.get("role_filter")
        post_date = request.POST.get("date_filter")
        print(post_date, post_date)
        print(request.POST)
        selected_role = post_role if post_role and post_role != "all" else None
        selected_date = post_date if post_date and post_date != "all" else None

    print(selected_role, selected_date)

    opportunity = Opportunity.objects.get(id=opp_id)
    is_matching_admin = OrganisationAdmin.objects.filter(user=request.user, organisation=opportunity.organisation).exists()

    if selected_role:
        selected_role_instance = Role.objects.get(id=selected_role)
        if selected_role_instance.opportunity.id != opportunity.id:
            raise ValidationError("Provided role is not part of viewed opportunity")
    else:
        selected_role_instance = None

    if selected_date:
        selected_date_instance = OneOffDate.objects.get(id=selected_date)
        if selected_date_instance.opportunity.id != opportunity.id:
            raise ValidationError("Provided date is not part of viewed opportunity")
    else:
        selected_date_instance = None

    if not is_matching_admin and not request.user.is_superuser:
        raise PermissionDenied("Authentication required.")

    shifts = iter_shift_triplets_for_opportunity(
        opportunity.id,
        selected_date_instance.id if selected_date_instance else None,
        selected_role_instance.id if selected_role_instance else None)


    shifts_list_dict = triplets_to_shift_dicts(shifts)
    unconfirmed_shifts = False

    for shift in shifts_list_dict:
        shift['available_volunteers'] = count_available_volunteers_for_oneoff(shift['schedule'], shift['role'])
        shift['assigned_volunteers'] = count_assigned_unconfirmed_active(shift['schedule'], shift['role'], shift['section'])
        shift['accepted_volunteers'] = count_sent_and_accepted(shift['schedule'], shift['role'], shift['section'])

        if shift['assigned_volunteers'] > 0 and unconfirmed_shifts == False:
            unconfirmed_shifts = True

    try:
        shifts_list_dict.sort(key=lambda d: d.get("available_volunteers", []))
    except Exception as e:
        print(f"[debug] Error: {e}")

    slots = (
        OneOffDate.objects
        .filter(opportunity=opportunity, date__gte=datetime.now())
        .values("date", "start_time", "end_time")
        .annotate(id=Min("id"))  # or Max("id")
        .order_by("date", "start_time", "end_time")
    )

    roles = Role.objects.filter(opportunity=opportunity)

    context = {
        'hx' : check_if_hx(request),
        'shifts' : shifts_list_dict,
        'slots' : slots,
        'opp' : opportunity,
        'unconfirmed_shifts' : unconfirmed_shifts,
        'selected_role': selected_role,
        'selected_date': selected_date,
        'roles': roles,
        'success' : success,
        'error' : error
    }

    return render(request, "org_admin/rota/shift_assignment.html", context)