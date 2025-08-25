from datetime import datetime, date, time
from typing import Optional, Iterable

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import IntegrityError, transaction
from django.db.models import Q
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.core.mail import send_mail
from threading import Thread

from organisations.models import Organisation
from commonui.views import check_if_hx
from opportunities.models import Opportunity, Registration
from org_admin.models import OrganisationAdmin
from rota.models import (
    Role,
    Section,
    VolunteerShift,
    OneOffDate,
    VolunteerOneOffDateAvailability,
    VolunteerRoleIntrest,
    Occurrence,
    Supervisor,
    RSVPChoices,
)

from django.contrib.auth.models import User



# ------------- Authorization & Utilities -------------

def require_authenticated(request: HttpRequest) -> None:
    """
    Ensure request.user is authenticated.
    """
    if not request.user or not request.user.is_authenticated:
        raise PermissionDenied("Authentication required.")


def user_is_superuser(request: HttpRequest) -> bool:
    """
    Superusers have full access.
    """
    return bool(request.user and request.user.is_superuser)


def get_admin_org(request: HttpRequest) -> Optional[Organisation]:
    """
    If the user is an OrganisationAdmin, return their organisation; else None.
    """
    is_admin = OrganisationAdmin.objects.filter(user=request.user).select_related("organisation").first()
    return is_admin.organisation if is_admin else None


def obj_organisation(obj) -> Optional[Organisation]:
    """
    Resolve an organisation from common rota/opportunity-related objects.
    """
    # Opportunity
    if isinstance(obj, Opportunity):
        return obj.organisation

    # Role
    if isinstance(obj, Role):
        return obj.opportunity.organisation

    # Section
    if isinstance(obj, Section):
        return obj.role.opportunity.organisation

    # OneOffDate
    if isinstance(obj, OneOffDate):
        return obj.opportunity.organisation

    # Occurrence
    if isinstance(obj, Occurrence):
        if obj.one_off_date:
            return obj.one_off_date.opportunity.organisation
        if obj.schedule and obj.schedule.opportunity:
            return obj.schedule.opportunity.organisation

    # Registration
    if isinstance(obj, Registration):
        return obj.opportunity.organisation

    # VolunteerShift
    if isinstance(obj, VolunteerShift):
        if obj.occurrence:
            return obj_organisation(obj.occurrence)
        # Fallback to role/opportunity
        if obj.role:
            return obj.role.opportunity.organisation

    # Supervisor
    if isinstance(obj, Supervisor):
        return obj.organisation

    return None


def assert_org_access(request: HttpRequest, *objects) -> None:
    """
    Ensure user is superuser or OrganisationAdmin for the target object's organisation.
    All provided objects must belong to the same organisation and match the admin's organisation.
    """
    require_authenticated(request)

    if user_is_superuser(request):
        return

    admin_org = get_admin_org(request)
    if not admin_org:
        raise PermissionDenied("Organisation admin access required.")

    for obj in objects:
        org = obj_organisation(obj)
        if not org or org.id != admin_org.id:
            raise PermissionDenied("Not authorized for this organisation.")


def safe_check_if_hx(request: Optional[HttpRequest] = None) -> bool:
    """
    Wrapper around check_if_hx that tolerates being called without arguments in some error paths.
    """
    try:
        return check_if_hx(request) if request is not None else check_if_hx()
    except TypeError:
        # Fallback if the implementation requires a request
        return False


# ------------- Core Business Helpers -------------

def send_email_to_volunteer(shift_id):
    shift = VolunteerShift.objects.get(id=shift_id)
    subject = 'Chip in System - Shift Assignment'

    section_name = "" if not shift.section else "Section Name: " + shift.section.name
    section_desc = "" if not shift.section else "Section Description: " + shift.section.description

    message = f"""
Hello {shift.registration.volunteer.user.first_name} {shift.registration.volunteer.user.last_name},

You have been assigned a shift for the opportunity: {shift.registration.opportunity.name}.

Shift Details:
Role: {shift.role.name}
Role description: {shift.role.description}
Role Volunteer Information: {shift.role.volunteer_description}
{section_name}
{section_desc}

Please login to the Chip In system to RSVP for the shift. You can access the screen by clicking the calendar icon at the bottom of the screen, then clicking shifts for the relevent opportunity.

Regards,
The Chip In Team
"""

    send_mail(subject, message, '', [shift.registration.volunteer.user.email], fail_silently=True)


class SendEmailToVolunteer(Thread):
    def __init__(self, shift_id):
        Thread.__init__(self)
        self.shift = shift_id

    def run(self):
        send_email_to_volunteer(self.shift)

def times_overlap(start_a: time, end_a: time, start_b: time, end_b: time) -> bool:
    """
    Return True if [start_a, end_a) overlaps with [start_b, end_b).
    Endpoints are treated as half-open to allow back-to-back shifts.
    """
    return start_a < end_b and end_a > start_b


def check_time_conflict(registration_id: int,
                        new_start_time: time,
                        new_end_time: time,
                        new_date: date,
                        exclude_shift_id: Optional[int] = None) -> bool:
    """
    Check if a volunteer has any existing shifts that conflict with the proposed time.
    Overlap is half-open: end == start is not considered an overlap.
    """
    if not registration_id or not new_start_time or not new_end_time or not new_date:
        return True  # Be conservative if data is missing

    existing_shifts = VolunteerShift.objects.filter(
        registration_id=registration_id,
        occurrence__date=new_date
    ).select_related("occurrence")

    if exclude_shift_id:
        existing_shifts = existing_shifts.exclude(id=exclude_shift_id)

    for shift in existing_shifts:
        if times_overlap(new_start_time, new_end_time, shift.occurrence.start_time, shift.occurrence.end_time):
            return True

    return False


def get_assigned_volunteers(schedule_id: int, role_id: int, section_id: Optional[int] = None):
    """
    Get volunteers already assigned to a specific shift (schedule+role [+optional section]).
    """
    try:
        role = Role.objects.select_related("opportunity__organisation").get(id=role_id)
        schedule = OneOffDate.objects.select_related("opportunity__organisation").get(id=schedule_id)

        registrations = Registration.objects.filter(opportunity=role.opportunity)
        active_registrations = [r.id for r in registrations if r.get_registration_status() == 'active']

        shift_filter = {
            'registration__in': active_registrations,
            'role': role,
            'occurrence__one_off_date': schedule,
        }

        if section_id:
            shift_filter['section_id'] = section_id
        else:
            shift_filter['section__isnull'] = True

        shifts = VolunteerShift.objects.filter(**shift_filter).values_list('registration_id', flat=True)
        if shifts:
            return Registration.objects.filter(id__in=shifts)
        return Registration.objects.none()
    except Exception:
        return Registration.objects.none()


def get_shift_volunteers(schedule_id: int, role_id: int):
    """
    Get volunteers available for a specific shift, excluding:
    - non-active registrations
    - users not available on the date
    - users not interested in the role
    - users with time conflicts on that date/time
    """
    try:
        role = Role.objects.select_related("opportunity__organisation").get(id=role_id)
        schedule = OneOffDate.objects.select_related("opportunity__organisation").get(id=schedule_id)

        registrations = Registration.objects.filter(opportunity=role.opportunity)
        active_registrations = [r.id for r in registrations if r.get_registration_status() == 'active']

        one_off_available_reg_ids = set(
            VolunteerOneOffDateAvailability.objects.filter(
                registration_id__in=active_registrations,
                one_off_date=schedule
            ).values_list('registration_id', flat=True)
        )
        role_interest_reg_ids = set(
            VolunteerRoleIntrest.objects.filter(
                registration_id__in=active_registrations,
                role=role
            ).values_list('registration_id', flat=True)
        )

        available_registrations = one_off_available_reg_ids.intersection(role_interest_reg_ids)

        if available_registrations:
            conflicted_volunteers = set()
            for reg_id in available_registrations:
                if check_time_conflict(reg_id, schedule.start_time, schedule.end_time, schedule.date):
                    conflicted_volunteers.add(reg_id)
            available_registrations.difference_update(conflicted_volunteers)

        if available_registrations:
            return Registration.objects.filter(id__in=available_registrations)
        return Registration.objects.none()
    except Exception:
        return Registration.objects.none()


def get_accepted_and_confirmed(schedule_id: int, role_id: int, section_id: Optional[int] = None):
    """
    Return [accepted_volunteers, confirmed_volunteers] as Registration QuerySets for a shift.
    """
    try:
        role = Role.objects.select_related("opportunity__organisation").get(id=role_id)
        schedule = OneOffDate.objects.select_related("opportunity__organisation").get(id=schedule_id)

        registrations = Registration.objects.filter(opportunity=role.opportunity)
        active_registrations = [r.id for r in registrations if r.get_registration_status() == 'active']

        base_filter = {
            'registration__in': active_registrations,
            'role': role,
            'occurrence__one_off_date': schedule,
            'confirmed': True
        }

        if section_id:
            base_filter['section_id'] = section_id
        else:
            base_filter['section__isnull'] = True

        confirmed_ids = VolunteerShift.objects.filter(**base_filter).values_list('registration_id', flat=True)
        confirmed_volunteers = Registration.objects.filter(id__in=confirmed_ids)

        accepted_filter = dict(base_filter)
        accepted_filter['rsvp_response'] = RSVPChoices.YES
        accepted_ids = VolunteerShift.objects.filter(**accepted_filter).values_list('registration_id', flat=True)
        accepted_volunteers = Registration.objects.filter(id__in=accepted_ids)

        return [accepted_volunteers, confirmed_volunteers]
    except Exception:
        return [Registration.objects.none(), Registration.objects.none()]


def get_available_volunteers_discrete(opportunity_id: int):
    """
    Build a list of shift blocks for per-role scheduling: each role has its own OneOffDate(s).
    """
    shifts = []
    roles = Role.objects.filter(opportunity=opportunity_id).select_related("opportunity__organisation")
    for role in roles:
        sections = Section.objects.filter(role=role)
        schedules = OneOffDate.objects.filter(role=role, date__gte=datetime.now().date()).select_related(
            "opportunity__organisation")
        for schedule in schedules:
            if sections.exists():
                for section in sections:
                    shifts.append({
                        'role': role,
                        'schedule': schedule,
                        'available_volunteers': get_shift_volunteers(schedule.id, role.id),
                        'assigned_volunteers': get_assigned_volunteers(schedule.id, role.id, section.id),
                        'accepted_volunteers': get_accepted_and_confirmed(schedule.id, role.id, section.id),
                        'section': section,
                    })
            else:
                shifts.append({
                    'role': role,
                    'schedule': schedule,
                    'available_volunteers': get_shift_volunteers(schedule.id, role.id),
                    'assigned_volunteers': get_assigned_volunteers(schedule.id, role.id),
                    'accepted_volunteers': get_accepted_and_confirmed(schedule.id, role.id),
                    'section': None,
                })
    return shifts


# ------------- Views -------------

@login_required
def supervisor_index(request: HttpRequest, error: Optional[str] = None) -> HttpResponse:
    """
    Display supervisor management index page.
    Only accessible to organisation admins or superusers.
    """
    require_authenticated(request)
    if user_is_superuser(request):
        # Superuser can view all supervisors; for safety, show none or require organisation selection.
        # Here, show none with a message if not an org admin too.
        admin_org = get_admin_org(request)
        supervisors = Supervisor.objects.filter(organisation=admin_org) if admin_org else Supervisor.objects.none()
        organisation = admin_org
    else:
        admin = OrganisationAdmin.objects.filter(user=request.user).select_related("organisation").first()
        if not admin:
            raise PermissionDenied("Organisation admin access required.")
        organisation = admin.organisation
        supervisors = Supervisor.objects.filter(organisation=organisation)

    context = {
        "organisation": organisation,
        'hx': safe_check_if_hx(request),
        'supervisors': supervisors,
        'error': error,
    }
    return render(request, 'org_admin/rota/rota_supervisor_index.html', context)


@login_required
def toggle_opportunity_scheduling_type(request: HttpRequest, opportunity_id: int) -> HttpResponse:
    """
    Toggle between SHARED and PER_ROLE scheduling modes for an opportunity.
    """
    require_authenticated(request)
    opportunity = get_object_or_404(Opportunity.objects.select_related("organisation"), id=opportunity_id)
    assert_org_access(request, opportunity)

    if opportunity.rota_config not in ("SHARED", "PER_ROLE"):
        # Default to SHARED if unexpected value, or set a safe default
        opportunity.rota_config = "SHARED"
    else:
        opportunity.rota_config = "PER_ROLE" if opportunity.rota_config == "SHARED" else "SHARED"
    opportunity.save()

    return opportunity_rota_index(request, opportunity_id)


@login_required
def unassign_volunteer_shift_instance(request: HttpRequest, registration_id: int, role_id: int) -> HttpResponse:
    """
    Remove a volunteer from a specific shift assignment.
    Requires org access to the underlying opportunity/occurrence.
    """
    require_authenticated(request)
    shift = VolunteerShift.objects.filter(
        registration_id=registration_id,
        role_id=role_id
    ).select_related("occurrence__one_off_date__opportunity__organisation", "role__opportunity__organisation").first()

    if not shift:
        # Nothing to unassign; just return the assignment page for the role if possible
        return assign_volunteer_shift(request, role_id, None, None)

    # Authorize via occurrence or role
    org = obj_organisation(shift)
    if not org:
        raise PermissionDenied("Invalid shift organisation.")
    assert_org_access(request, shift)

    # Capture route params for the return view
    role_id = shift.role.id
    schedule_id = shift.occurrence.one_off_date.id if shift.occurrence.one_off_date else None
    section_id = shift.section.id if shift.section else None

    shift.delete()

    return assign_volunteer_shift(request, role_id, schedule_id, section_id)


@login_required
def assign_volunteer_shift_instance(request: HttpRequest, registration_id: int, role_id: int,
                                    schedule_id: int, section_id: Optional[int] = None) -> HttpResponse:
    """
    Assign a volunteer to a specific shift with time conflict validation.
    Enforces:
    - Organisation access
    - Active registration
    - Availability for date and interest in role
    - No existing conflicting shifts on that date/time
    - No duplicate assignment to the same occurrence/section
    """
    require_authenticated(request)
    try:
        role = Role.objects.select_related("opportunity__organisation").get(id=role_id)
        schedule = OneOffDate.objects.select_related("opportunity__organisation").get(id=schedule_id)
        registration = Registration.objects.select_related("opportunity__organisation").get(id=registration_id)
        section = Section.objects.get(id=section_id) if section_id else None
    except (Role.DoesNotExist, OneOffDate.DoesNotExist, Registration.DoesNotExist, Section.DoesNotExist):
        return render(request, 'org_admin/error.html', {'error': 'Invalid role/schedule/registration/section.'})

    # Auth: require org match
    assert_org_access(request, role, schedule, registration)
    if section:
        assert_org_access(request, section)

    # Verify eligible for this shift
    eligible_qs = get_shift_volunteers(schedule.id, role.id)
    if not eligible_qs.filter(id=registration_id).exists():
        return assign_volunteer_shift(request, role_id, schedule_id, section_id)

    # Prevent duplicates: same occurrence + same registration (+ same section/null)
    # Ensure occurrence exists or create it atomically
    with transaction.atomic():
        occ, _ = Occurrence.objects.get_or_create(
            one_off_date=schedule,
            defaults={
                'date': schedule.date,
                'start_time': schedule.start_time,
                'end_time': schedule.end_time,
            }
        )

        # Extra conflict check across the same date/time
        if check_time_conflict(registration_id, schedule.start_time, schedule.end_time, schedule.date):
            return assign_volunteer_shift(request, role_id, schedule_id, section_id)

        # Create shift or no-op if exists (unique_together on registration+occurrence)
        try:
            shift, created = VolunteerShift.objects.get_or_create(
                registration=registration,
                occurrence=occ,
                defaults={'role': role, 'section': section}
            )
            if not created:
                # Update role/section if needed for this occurrence; prevent moving to a conflicting section
                if shift.role_id != role.id or (shift.section_id or None) != (section.id if section else None):
                    # If role differs, ensure user meets role interest
                    if shift.role_id != role.id:
                        if not VolunteerRoleIntrest.objects.filter(registration=registration, role=role).exists():
                            return assign_volunteer_shift(request, role_id, schedule_id, section_id)
                    shift.role = role
                    shift.section = section
                    shift.save()
        except IntegrityError:
            # Race condition fallback: shift exists
            pass

    return assign_volunteer_shift(request, role_id, schedule_id, section_id)


@login_required
def assign_volunteer_shift(request: HttpRequest, role_id: int,
                           schedule_id: Optional[int], section_id: Optional[int] = None) -> HttpResponse:
    """
    Display the volunteer shift assignment interface for a specific role/schedule combination.
    """
    require_authenticated(request)
    try:
        role = Role.objects.select_related("opportunity__organisation").get(id=role_id)
        schedule = OneOffDate.objects.select_related("opportunity__organisation").get(id=schedule_id) if schedule_id else None
    except Exception as e:
        return render(request, 'org_admin/error.html', {'error': f'Failed to get role/schedule: {e}'})

    # Authorize on role and schedule (if provided)
    if schedule:
        assert_org_access(request, role, schedule)
    else:
        assert_org_access(request, role)

    opportunity = role.opportunity

    registrations = get_shift_volunteers(schedule.id, role.id) if schedule else Registration.objects.none()
    assigned_volunteers = get_assigned_volunteers(schedule.id, role.id, section_id) if schedule else Registration.objects.none()

    context = {
        'hx': safe_check_if_hx(request),
        'opp': opportunity,
        'registrations': registrations,
        'assigned_volunteers': assigned_volunteers,
        'schedule_id': schedule.id if schedule else None,
        'section_id': section_id,
        'role_id': role.id,
    }
    return render(request, 'org_admin/rota/volunteer_shift_assignment.html', context)


@login_required
def assign_rota(request: HttpRequest, opp_id: int, success: Optional[str] = None, error: Optional[str] = None) -> HttpResponse:
    """
    Display the main shift assignment interface for an opportunity.
    Shows all shifts that need volunteers assigned.
    """
    require_authenticated(request)
    opportunity = get_object_or_404(Opportunity.objects.select_related("organisation"), id=opp_id)
    assert_org_access(request, opportunity)

    shifts = []
    if getattr(opportunity, "rota_config", "SHARED") == "SHARED":
        # Shared scheduling: same dates across all roles
        schedules = OneOffDate.objects.filter(
            opportunity=opportunity,
            date__gte=datetime.now().date(),
            role__isnull=True
        ).select_related("opportunity__organisation")

        roles = Role.objects.filter(opportunity=opp_id).select_related("opportunity__organisation")
        for schedule in schedules:
            for role in roles:
                sections = Section.objects.filter(role=role)
                available_volunteers = get_shift_volunteers(schedule.id, role.id)
                if sections.exists():
                    for section in sections:
                        shifts.append({
                            'section': section,
                            'role': role,
                            'schedule': schedule,
                            'available_volunteers': available_volunteers,
                            'assigned_volunteers': get_assigned_volunteers(schedule.id, role.id, section.id),
                            'accepted_volunteers': get_accepted_and_confirmed(schedule.id, role.id, section.id),
                        })
                else:
                    shifts.append({
                        'role': role,
                        'schedule': schedule,
                        'section': None,
                        'available_volunteers': available_volunteers,
                        'assigned_volunteers': get_assigned_volunteers(schedule.id, role.id),
                        'accepted_volunteers': get_accepted_and_confirmed(schedule.id, role.id),
                    })
    else:
        shifts = get_available_volunteers_discrete(opportunity.id)

    unconfirmed_shifts = VolunteerShift.objects.filter(
        registration__opportunity=opportunity,
        confirmed=False
    ).exists()

    context = {
        'hx': safe_check_if_hx(request),
        'shifts': shifts,
        'opp': opportunity,
        'unconfirmed_shifts': unconfirmed_shifts,
        'success': success,
        'error': error,
    }
    return render(request, "org_admin/rota/shift_assignment.html", context)


@login_required
def edit_rota_schedule(request: HttpRequest, opp_id: Optional[int] = None,
                       schedule_id: Optional[int] = None, role_id: Optional[int] = None) -> HttpResponse:
    """
    Handle creation and editing of schedule dates.
    """
    require_authenticated(request)

    if request.method == "POST":
        if not schedule_id:
            return create_schedule(request, opp_id, role_id)
        else:
            return edit_schedule(request, schedule_id)

    opportunity = None
    schedule = None

    if opp_id:
        opportunity = get_object_or_404(Opportunity.objects.select_related("organisation"), id=opp_id)
        assert_org_access(request, opportunity)

    if schedule_id:
        schedule = get_object_or_404(OneOffDate.objects.select_related("opportunity__organisation"), id=schedule_id)
        assert_org_access(request, schedule)
        opportunity = schedule.opportunity

    context = {
        'hx': safe_check_if_hx(request),
        'schedule': schedule,
        'opp': opportunity.id if opportunity else None,
        'role': role_id if role_id else None,
    }
    return render(request, "org_admin/rota/one_off_schedule_editor.html", context)


@login_required
def create_schedule(request: HttpRequest, opp_id: int, role_id: Optional[int] = None) -> HttpResponse:
    """
    Create a new one-off schedule date for an opportunity (optionally per role).
    """
    require_authenticated(request)
    opportunity = get_object_or_404(Opportunity.objects.select_related("organisation"), id=opp_id)
    assert_org_access(request, opportunity)
    role = None
    if role_id:
        role = get_object_or_404(Role.objects.select_related("opportunity__organisation"), id=role_id)
        assert_org_access(request, role)
        if role.opportunity_id != opportunity.id:
            return render(request, 'org_admin/error.html', {'error': 'Role does not belong to the opportunity.'})

    try:
        schedule = OneOffDate(
            date=request.POST.get('schedule_date'),
            start_time=request.POST.get('schedule_start_time'),
            end_time=request.POST.get('schedule_end_time'),
            opportunity=opportunity,
            role=role,
        )
        schedule.full_clean()
        schedule.save()
        request.method = 'GET'
        if schedule.role:
            return edit_role(request, schedule.role.id)
        else:
            return opportunity_rota_index(request, opp_id)
    except ValidationError as ve:
        return render(request, 'org_admin/error.html', {'error': f'Validation error: {ve.message_dict}'})
    except Exception as e:
        return render(request, 'org_admin/error.html', {'error': f'Failed to create schedule: {str(e)}'})


@login_required
def edit_schedule(request: HttpRequest, schedule_id: int) -> HttpResponse:
    """
    Update an existing one-off schedule date.
    """
    require_authenticated(request)
    schedule = get_object_or_404(OneOffDate.objects.select_related("opportunity__organisation"), id=schedule_id)
    assert_org_access(request, schedule)

    try:
        schedule.date = request.POST.get('schedule_date')
        schedule.start_time = request.POST.get('schedule_start_time')
        schedule.end_time = request.POST.get('schedule_end_time')
        schedule.full_clean()
        schedule.save()
        request.method = "GET"
        if schedule.role:
            return edit_role(request, schedule.role.id)
        else:
            return opportunity_rota_index(request, schedule.opportunity.id)
    except ValidationError as ve:
        return render(request, 'org_admin/error.html', {'error': f'Validation error: {ve.message_dict}'})
    except Exception as e:
        return render(request, 'org_admin/error.html', {'error': f'Failed to update schedule: {str(e)}'})


@login_required
def rota_index(request: HttpRequest) -> HttpResponse:
    """
    Display main rota management page showing all opportunities
    scoped to the admin's organisation; superusers see none here unless they are also an admin.
    """
    require_authenticated(request)
    admin = OrganisationAdmin.objects.filter(user=request.user).select_related("organisation").first()
    if admin:
        opportunities = Opportunity.objects.filter(organisation=admin.organisation)
        context = {
            'hx': safe_check_if_hx(request),
            'opportunities': opportunities
        }
        return render(request, "org_admin/rota/rota_index.html", context)
    elif user_is_superuser(request):
        # Optional: Superuser without admin org – show nothing or redirect.
        context = {
            'hx': safe_check_if_hx(request),
            'opportunities': Opportunity.objects.none()
        }
        return render(request, "org_admin/rota/rota_index.html", context)
    else:
        raise PermissionDenied("Organisation admin access required.")


@login_required
def edit_section(request: HttpRequest, role_id: Optional[int] = None, section_id: Optional[int] = None) -> HttpResponse:
    """
    Handle creation and editing of role sections.
    """
    require_authenticated(request)

    if request.method == "POST":
        if section_id is not None:
            return save_section(request, section_id)
        if role_id is not None:
            return create_new_section(request, role_id)

    section = None
    role = None

    if section_id:
        section = get_object_or_404(Section.objects.select_related("role__opportunity__organisation"), id=section_id)
        assert_org_access(request, section)
        role = section.role

    if role_id and role is None:
        role = get_object_or_404(Role.objects.select_related("opportunity__organisation"), id=role_id)
        assert_org_access(request, role)

    context = {
        'hx': safe_check_if_hx(request),
        'role': role,
        'section': section,
    }
    return render(request, "org_admin/rota/section_editor.html", context)


@login_required
def save_section(request: HttpRequest, section_id: int) -> HttpResponse:
    """
    Save changes to an existing section.
    """
    require_authenticated(request)
    section = get_object_or_404(Section.objects.select_related("role__opportunity__organisation"), id=section_id)
    assert_org_access(request, section)

    try:
        section.name = request.POST.get('section_name', '')
        section.description = request.POST.get('section_description', '')
        section.required_volunteers = int(request.POST.get('section_volunteers', 0))
        if section.required_volunteers < 0:
            raise ValidationError("required_volunteers cannot be negative.")
        section.save()
        request.method = 'GET'
        return edit_role(request, section.role_id)
    except ValidationError as ve:
        return render(request, 'org_admin/error.html', {'error': f'Validation error: {ve}'})
    except Exception as e:
        return render(request, 'org_admin/error.html', {'error': f'Failed to save section: {str(e)}'})


@login_required
def create_new_section(request: HttpRequest, role_id: int) -> HttpResponse:
    """
    Create a new section for a role.
    """
    require_authenticated(request)
    role = get_object_or_404(Role.objects.select_related("opportunity__organisation"), id=role_id)
    assert_org_access(request, role)

    try:
        required_volunteers = int(request.POST.get('section_volunteers', 0))
        if required_volunteers < 0:
            raise ValidationError("required_volunteers cannot be negative.")

        section = Section(
            name=request.POST.get('section_name', ''),
            description=request.POST.get('section_description', ''),
            required_volunteers=required_volunteers,
            role=role,
        )
        section.full_clean()
        section.save()
        request.method = 'GET'
        return edit_role(request, role_id)
    except ValidationError as ve:
        return render(request, 'org_admin/error.html', {'error': f'Validation error: {ve.message_dict if hasattr(ve, "message_dict") else ve}'})
    except Exception as e:
        return render(request, 'org_admin/error.html', {'error': f'Failed to create section: {str(e)}'})


@login_required
def edit_role(request: HttpRequest, role_id: Optional[int] = None, opp_id: Optional[int] = None) -> HttpResponse:
    """
    Handle creation and editing of volunteer roles.
    """
    require_authenticated(request)

    if request.method == "POST":
        if role_id is not None:
            return save_role(request, role_id)
        if opp_id is not None:
            create_new_rota_role(request, opp_id)
            return opportunity_rota_index(request, opp_id)

    role = None
    sections = None
    volunteers_required = None
    one_off_dates = None
    opp = None

    if role_id:
        role = get_object_or_404(Role.objects.select_related("opportunity__organisation"), id=role_id)
        assert_org_access(request, role)
        opp = role.opportunity
        sections = Section.objects.filter(role=role)
        volunteers_required = sum(section.required_volunteers for section in sections)
        one_off_dates = OneOffDate.objects.filter(role=role)
    elif opp_id:
        opp = get_object_or_404(Opportunity.objects.select_related("organisation"), id=opp_id)
        assert_org_access(request, opp)

    context = {
        "hx": safe_check_if_hx(request),
        "opp": opp,
        "role": role,
        "sections": sections,
        "volunteers_required": volunteers_required,
        "one_off_dates": one_off_dates,
    }
    return render(request, "org_admin/rota/role_editor.html", context)


@login_required
def create_new_rota_role(request: HttpRequest, opp_id: int) -> HttpResponse:
    """
    Create a new volunteer role under an opportunity.
    """
    require_authenticated(request)
    opportunity = get_object_or_404(Opportunity.objects.select_related("organisation"), id=opp_id)
    assert_org_access(request, opportunity)

    try:
        required_volunteers = int(request.POST.get("role_volunteers", 0))
        if required_volunteers < 0:
            raise ValidationError("required_volunteers cannot be negative.")

        role = Role(
            name=request.POST.get("role_name", ""),
            description=request.POST.get("role_description", ""),
            volunteer_description=request.POST.get("volunteer_description", ""),
            required_volunteers=required_volunteers,
            opportunity=opportunity,
        )
        role.full_clean()
        role.save()
        return opportunity_rota_index(request, opp_id)
    except ValidationError as ve:
        return render(request, 'org_admin/error.html', {'error': f'Validation error: {ve.message_dict if hasattr(ve, "message_dict") else ve}'})
    except Exception as e:
        return render(request, 'org_admin/error.html', {'error': f'Failed to create role: {str(e)}'})


@login_required
def save_role(request: HttpRequest, role_id: int) -> HttpResponse:
    """
    Save changes to an existing role.
    Only update role.required_volunteers if the role has no sections.
    """
    require_authenticated(request)
    role = get_object_or_404(Role.objects.select_related("opportunity__organisation"), id=role_id)
    assert_org_access(request, role)

    try:
        role.name = request.POST.get("role_name", "")
        role.description = request.POST.get("role_description", "")
        role.volunteer_description = request.POST.get("volunteer_description", "")

        if Section.objects.filter(role=role).count() == 0:
            new_required = int(request.POST.get("role_volunteers", 0))
            if new_required < 0:
                raise ValidationError("required_volunteers cannot be negative.")
            role.required_volunteers = new_required

        role.full_clean()
        role.save()
        request.method = 'GET'
        return edit_role(request, role.id)
    except ValidationError as ve:
        return render(request, 'org_admin/error.html', {'error': f'Validation error: {ve.message_dict if hasattr(ve, "message_dict") else ve}'})
    except Exception as e:
        return render(request, 'org_admin/error.html', {'error': f'Failed to save role: {str(e)}'})


@login_required
def opportunity_rota_index(request: HttpRequest, opportunity_id: int,
                           error: Optional[str] = None, success: Optional[str] = None) -> HttpResponse:
    """
    Display rota management page for a specific opportunity.
    """
    require_authenticated(request)
    opportunity = get_object_or_404(Opportunity.objects.select_related("organisation"), id=opportunity_id)
    assert_org_access(request, opportunity)

    schedules = OneOffDate.objects.filter(opportunity=opportunity, role=None)
    roles = Role.objects.filter(opportunity=opportunity)

    context = {
        'opportunity': opportunity,
        'schedules': schedules,
        'roles': roles,
        'error': error,
        'success': success,
        'hx': safe_check_if_hx(request),
    }
    return render(request, "org_admin/rota/rota_opp_index.html", context)


@login_required
def confirm_shifts(request: HttpRequest, opp_id: int) -> HttpResponse:
    """
    Confirm all unconfirmed shifts for an opportunity and notify volunteers.
    """
    require_authenticated(request)
    opportunity = get_object_or_404(Opportunity.objects.select_related("organisation"), id=opp_id)
    assert_org_access(request, opportunity)

    try:
        count = 0
        unconfirmed_shifts = VolunteerShift.objects.filter(
            registration__opportunity=opportunity,
            confirmed=False
        ).select_related("registration")

        for shift in unconfirmed_shifts:
            shift.confirmed = True
            shift.save()

            email_thread = SendEmailToVolunteer(shift.id)
            email_thread.start()

            count += 1

        return assign_rota(request, opportunity.id, success=f"Sent shifts to {count} volunteers.")
    except Exception:
        return assign_rota(request, opp_id, error="Failed to confirm shifts. Please try again.")


@login_required
def edit_supervisor(request: HttpRequest, supervisor_id: Optional[int]):
    """
    View to edit a supervisor's scope.
    Only for admins of the supervisor's organisation or superusers.
    """
    require_authenticated(request)

    admin = OrganisationAdmin.objects.filter(user=request.user).select_related("organisation").first()
    sup = None
    sup_opps = None
    sup_roles = None
    sup_shifts = None

    if supervisor_id:
        try:
            sup = Supervisor.objects.select_related("organisation", "user").get(id=supervisor_id)
            assert_org_access(request, sup)  # enforce org
            sup_opps = sup.supervisor_opportunities.values_list('id', flat=True)
            sup_roles = sup.supervisor_roles.values_list('id', flat=True)
            sup_shifts = sup.supervisor_shifts.values_list('id', flat=True)
        except Supervisor.DoesNotExist:
            sup = None

    opportunities = Opportunity.objects.filter(organisation=admin.organisation) if admin else Opportunity.objects.none()
    roles = Role.objects.filter(opportunity__organisation=admin.organisation) if admin else Role.objects.none()
    shifts = Occurrence.objects.filter(
        one_off_date__opportunity__organisation=admin.organisation,
        one_off_date__date__gt=datetime.now().date()
    ) if admin else Occurrence.objects.none()

    context = {
        'sup': sup,
        'hx': safe_check_if_hx(request),
        'sup_roles': sup_roles,
        'sup_shifts': sup_shifts,
        'sup_opps': sup_opps,
        'roles': roles,
        'shifts': shifts,
        'opportunities': opportunities
    }
    return render(request, "org_admin/rota/add_edit_supervisor.html", context)


@login_required
def add_supervisor(request: HttpRequest):
    """
    Create a supervisor record for the admin's organisation.
    """
    require_authenticated(request)

    if request.method == 'POST':
        return save_supervisor(request)

    context = {
        'hx': safe_check_if_hx(request)
    }
    return render(request, "org_admin/rota/add_edit_supervisor.html", context)


@login_required
def partial_opp_picker(request: HttpRequest, supervisor_id: Optional[int] = None):
    """
    Partial view listing opportunities for selection; restricted to caller's organisation.
    """
    require_authenticated(request)
    admin = OrganisationAdmin.objects.filter(user=request.user).select_related("organisation").first()
    if not admin and not user_is_superuser(request):
        raise PermissionDenied("Organisation admin access required.")

    sup_opps = None
    if supervisor_id:
        try:
            sup = Supervisor.objects.select_related("organisation").get(id=supervisor_id)
            assert_org_access(request, sup)
            sup_opps = sup.supervisor_opportunities.values_list('id', flat=True)
        except Supervisor.DoesNotExist:
            sup_opps = None

    opportunities = Opportunity.objects.filter(organisation=admin.organisation) if admin else Opportunity.objects.none()

    context = {
        'hx': safe_check_if_hx(request),
        'opportunities': opportunities,
        'sup_opps': sup_opps
    }
    return render(request, "org_admin/rota/partials/opp_picker.html", context)


@login_required
def partial_role_picker(request: HttpRequest, supervisor_id: Optional[int] = None):
    """
    Partial view listing roles for selection; restricted to caller's organisation.
    """
    require_authenticated(request)
    admin = OrganisationAdmin.objects.filter(user=request.user).select_related("organisation").first()
    if not admin and not user_is_superuser(request):
        raise PermissionDenied("Organisation admin access required.")

    sup_roles = None
    if supervisor_id:
        try:
            sup = Supervisor.objects.select_related("organisation").get(id=supervisor_id)
            assert_org_access(request, sup)
            sup_roles = sup.supervisor_roles.values_list('id', flat=True)
        except Supervisor.DoesNotExist:
            sup_roles = None

    roles = Role.objects.filter(opportunity__organisation=admin.organisation) if admin else Role.objects.none()

    context = {
        'hx': safe_check_if_hx(request),
        'roles': roles,
        'sup_roles': sup_roles
    }
    return render(request, "org_admin/rota/partials/role_picker.html", context)


@login_required
def partial_shift_picker(request: HttpRequest, supervisor_id: Optional[int] = None):
    """
    Partial view listing shifts (occurrences) for selection; restricted to caller's organisation.
    """
    require_authenticated(request)
    admin = OrganisationAdmin.objects.filter(user=request.user).select_related("organisation").first()
    if not admin and not user_is_superuser(request):
        raise PermissionDenied("Organisation admin access required.")

    sup_shifts = None
    if supervisor_id:
        try:
            sup = Supervisor.objects.select_related("organisation").get(id=supervisor_id)
            assert_org_access(request, sup)
            sup_shifts = sup.supervisor_shifts.values_list('id', flat=True)
        except Supervisor.DoesNotExist:
            sup_shifts = None

    shifts = Occurrence.objects.filter(
        one_off_date__opportunity__organisation=admin.organisation,
        one_off_date__date__gt=datetime.now().date()
    ) if admin else Occurrence.objects.none()

    context = {
        'shifts': shifts,
        'hx': safe_check_if_hx(request),
        'sup_shifts': sup_shifts
    }
    return render(request, "org_admin/rota/partials/shift_picker.html", context)


@login_required
def save_supervisor(request: HttpRequest, supervisor_id: Optional[int] = None):
    """
    Create or update a supervisor under the admin's organisation.
    Accepts access_type in ['all_org', 'opp', 'roles', 'shifts'] and validates posted IDs belong to the same organisation.
    """
    require_authenticated(request)
    admin = OrganisationAdmin.objects.filter(user=request.user).select_related("organisation").first()
    if not admin and not user_is_superuser(request):
        raise PermissionDenied("Organisation admin access required.")

    data = request.POST
    supervisor = None

    # Create if not exists
    if not supervisor_id:
        email = data.get('sup_email')
        if not email:
            return supervisor_index(request, error="Enter valid email!")

        user = User.objects.filter(email=email).first()
        if user:
            # Ensure no existing supervisor for this org
            if Supervisor.objects.filter(organisation=(admin.organisation if admin else None), user=user).exists():
                return supervisor_index(request, error="User already exists as a supervisor")

            supervisor = Supervisor(user=user, organisation=(admin.organisation if admin else None))
            supervisor.full_clean()
            supervisor.save()
        else:
            # Create user
            user = User.objects.create_user(username=email, email=email)
            user.set_unusable_password()
            user.save()
            supervisor = Supervisor(user=user, organisation=(admin.organisation if admin else None))
            supervisor.full_clean()
            supervisor.save()
    else:
        supervisor = get_object_or_404(Supervisor.objects.select_related("organisation"), id=supervisor_id)
        assert_org_access(request, supervisor)

    # At this point supervisor must exist
    if not supervisor:
        return supervisor_index(request, error="Failed to create supervisor")

    # Access type handling
    access_level = data.get('access_type')
    if access_level not in ('all_org', 'opp', 'roles', 'shifts'):
        return supervisor_index(request, error="Invalid access type")

    try:
        if access_level == 'all_org':
            supervisor.access_level = 'all_org'
            supervisor.supervisor_opportunities.clear()
            supervisor.supervisor_roles.clear()
            supervisor.supervisor_shifts.clear()

        elif access_level == 'opp':
            supervisor.access_level = 'all_opportunity'
            opp_ids = data.getlist('opp_select')
            if not opp_ids:
                return supervisor_index(request, error="Select at least one opportunity")
            # Validate org scope
            opps = Opportunity.objects.filter(id__in=opp_ids, organisation=supervisor.organisation)
            if opps.count() != len(opp_ids):
                return supervisor_index(request, error="Invalid opportunities for this organisation")
            supervisor.supervisor_opportunities.set(opps)
            supervisor.supervisor_roles.clear()
            supervisor.supervisor_shifts.clear()

        elif access_level == 'roles':
            supervisor.access_level = 'all_role'
            role_ids = data.getlist('role_select')
            if not role_ids:
                return supervisor_index(request, error="Select at least one role")
            roles = Role.objects.filter(id__in=role_ids, opportunity__organisation=supervisor.organisation)
            if roles.count() != len(role_ids):
                return supervisor_index(request, error="Invalid roles for this organisation")
            supervisor.supervisor_roles.set(roles)
            supervisor.supervisor_opportunities.clear()
            supervisor.supervisor_shifts.clear()

        elif access_level == 'shifts':
            supervisor.access_level = 'specific_shifts'
            shift_ids = data.getlist('shift_select')
            if not shift_ids:
                return supervisor_index(request, error="Select at least one shift")
            shifts = Occurrence.objects.filter(
                id__in=shift_ids,
                one_off_date__opportunity__organisation=supervisor.organisation
            )
            if shifts.count() != len(shift_ids):
                return supervisor_index(request, error="Invalid shifts for this organisation")
            supervisor.supervisor_shifts.set(shifts)
            supervisor.supervisor_opportunities.clear()
            supervisor.supervisor_roles.clear()

        supervisor.full_clean()
        supervisor.save()
        return supervisor_index(request)
    except ValidationError as ve:
        return supervisor_index(request, error=f"Validation error: {ve}")
    except Exception:
        return supervisor_index(request, error="Failed to save supervisor")


# ------------- Additional Helper Routes -------------

@login_required
def confirm_shifts_for_occurrence(request: HttpRequest, occurrence_id: int) -> HttpResponse:
    """
    Example helper: confirm shifts for a single occurrence.
    Ensures org access via occurrence -> one_off_date -> opportunity -> organisation.
    """
    require_authenticated(request)
    occ = get_object_or_404(Occurrence.objects.select_related("one_off_date__opportunity__organisation"), id=occurrence_id)
    assert_org_access(request, occ)

    updated = VolunteerShift.objects.filter(occurrence=occ, confirmed=False).update(confirmed=True)
    return redirect('rota:shift_assignment_for_occurrence', occurrence_id=occurrence_id)


