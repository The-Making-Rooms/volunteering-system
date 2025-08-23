from datetime import datetime, time
from logging import exception
from django.shortcuts import render
from django.db.models import Q
from organisations.models import Organisation
from commonui.views import check_if_hx
from opportunities.models import Opportunity, Registration
from org_admin.models import OrganisationAdmin
from rota.models import Role, Section, VolunteerShift, OneOffDate, VolunteerOneOffDateAvailability, \
    VolunteerRoleIntrest, Occurrence, Supervisor
from django.contrib.auth.models import User

def supervisor_index(request, error=None):
    """
    Display supervisor management index page.
    Only accessible to organisation admins.
    """
    is_admin = OrganisationAdmin.objects.filter(user=request.user)

    if is_admin.exists():
        organisation = is_admin.first().organisation
        supervisors = Supervisor.objects.filter(organisation=organisation)

        context = {
            "organisation": organisation,
            'hx': check_if_hx(request),
            'supervisors': supervisors,
            'error' : error
        }

        return render(
            request,
            'org_admin/rota/rota_supervisor_index.html',
            context
        )
    else:
        return render(
            request,
            "org_admin/no_admin.html",
            context={'hx': check_if_hx()}
        )


def toggle_opportunity_scheduling_type(request, opportunity_id):
    """
    Toggle between SHARED and PER_ROLE scheduling modes for an opportunity.
    """
    opportunity = Opportunity.objects.get(id=opportunity_id)

    if opportunity.rota_config == "SHARED":
        opportunity.rota_config = "PER_ROLE"
    elif opportunity.rota_config == "PER_ROLE":
        opportunity.rota_config = "SHARED"

    opportunity.save()
    return opportunity_rota_index(request, opportunity_id)


def check_time_conflict(registration_id, new_start_time, new_end_time, new_date, exclude_shift_id=None):
    """
    Check if a volunteer has any existing shifts that conflict with the proposed time.

    Args:
        registration_id: ID of the volunteer registration
        new_start_time: Start time of new shift
        new_end_time: End time of new shift
        new_date: Date of new shift
        exclude_shift_id: Optional shift ID to exclude from conflict check (for updates)

    Returns:
        Boolean indicating if there's a time conflict
    """
    # Get all existing shifts for this volunteer on the same date
    existing_shifts = VolunteerShift.objects.filter(
        registration_id=registration_id,
        occurrence__date=new_date
    )

    if exclude_shift_id:
        existing_shifts = existing_shifts.exclude(id=exclude_shift_id)

    # Check for time overlaps
    for shift in existing_shifts:
        existing_start = shift.occurrence.start_time
        existing_end = shift.occurrence.end_time

        # Check if times overlap
        if (new_start_time < existing_end and new_end_time > existing_start):
            return True

    return False


def unassign_volunteer_shift_instance(request, registration_id, role_id):
    """
    Remove a volunteer from a specific shift assignment.
    """
    try:
        shift = VolunteerShift.objects.filter(
            registration_id=registration_id,
            role_id=role_id
        ).first()

        if not shift:
            print(f"[Error]: No shift found for registration {registration_id} and role {role_id}")
            return assign_volunteer_shift(request, role_id, None, None)

        role_id = shift.role.id
        schedule_id = shift.occurrence.one_off_date.id
        section_id = shift.section.id if shift.section else None

        shift.delete()
        print(f"[Info]: Successfully unassigned volunteer {registration_id} from shift")

        return assign_volunteer_shift(request, role_id, schedule_id, section_id)

    except Exception as e:
        print(f"[Error]: Failed to unassign volunteer shift: {e}")
        return assign_volunteer_shift(request, role_id, None, None)


def assign_volunteer_shift_instance(request, registration_id, role_id, schedule_id, section_id=None):
    """
    Assign a volunteer to a specific shift with time conflict validation.

    Args:
        registration_id: ID of volunteer registration
        role_id: ID of role
        schedule_id: ID of schedule/date
        section_id: Optional section ID
    """
    print(
        f"[Info]: Assigning volunteer {registration_id} to role {role_id}, schedule {schedule_id}, section {section_id}")

    try:
        # Get required objects
        role = Role.objects.get(id=role_id)
        schedule = OneOffDate.objects.get(id=schedule_id)
        registration = Registration.objects.get(id=registration_id)
        section = Section.objects.get(id=section_id) if section_id else None
        opportunity = role.opportunity

    except Exception as e:
        print(f"[Error]: Failed to get required objects: {e}")
        return assign_volunteer_shift(request, role_id, schedule_id, section_id)

    # Verify volunteer is eligible for this shift
    volunteer_registrations = get_shift_volunteers(schedule.id, role.id)
    if registration_id not in volunteer_registrations.values_list('id', flat=True):
        print(f"[Error]: Volunteer {registration_id} is not available for this shift")
        return assign_volunteer_shift(request, role_id, schedule_id, section_id)

    # Check for time conflicts
    if check_time_conflict(registration_id, schedule.start_time, schedule.end_time, schedule.date):
        print(f"[Error]: Volunteer {registration_id} has a conflicting shift at this time")
        return assign_volunteer_shift(request, role_id, schedule_id, section_id)

    # Check if volunteer is already assigned to this exact shift
    existing_shift = VolunteerShift.objects.filter(
        registration_id=registration_id,
        role_id=role_id,
        occurrence__one_off_date_id=schedule_id,
        section=section
    ).first()

    if existing_shift:
        print(f"[Warning]: Volunteer {registration_id} already assigned to this shift")
        return assign_volunteer_shift(request, role_id, schedule_id, section_id)

    # Get or create occurrence
    occurrence, created = Occurrence.objects.get_or_create(
        one_off_date=schedule,
        defaults={
            'date': schedule.date,
            'start_time': schedule.start_time,
            'end_time': schedule.end_time,
        }
    )

    if created:
        print(f"[Info]: Created new occurrence for schedule {schedule_id}")

    # Create the shift assignment
    shift = VolunteerShift.objects.create(
        registration=registration,
        occurrence=occurrence,
        role=role,
        section=section,
    )

    print(f"[Info]: Successfully assigned volunteer {registration_id} to shift {shift.id}")
    return assign_volunteer_shift(request, role_id, schedule_id, section_id)


def assign_volunteer_shift(request, role_id, schedule_id, section_id=None):
    """
    Display the volunteer shift assignment interface for a specific role/schedule combination.
    """
    print(f"[Debug]: assign_volunteer_shift - role: {role_id}, schedule: {schedule_id}, section: {section_id}")

    try:
        role = Role.objects.get(id=role_id)
        schedule = OneOffDate.objects.get(id=schedule_id) if schedule_id else None
        opportunity = role.opportunity

    except Exception as e:
        print(f"[Error]: Failed to get role/schedule objects: {e}")
        return render(request, 'org_admin/error.html', {'error': str(e)})

    # Get available and assigned volunteers
    volunteer_registrations = get_shift_volunteers(schedule.id, role.id) if schedule else []
    assigned_volunteers = get_assigned_volunteers(schedule.id, role.id, section_id) if schedule else []

    context = {
        'hx': check_if_hx(request),
        'opp': opportunity,
        'registrations': volunteer_registrations,
        'assigned_volunteers': assigned_volunteers,
        'schedule_id': schedule.id if schedule else None,
        'section_id': section_id,
        'role_id': role.id,
    }

    return render(request, 'org_admin/rota/volunteer_shift_assignment.html', context)


def assign_rota(request, opp_id, success=None, error=None):
    """
    Display the main shift assignment interface for an opportunity.
    Shows all shifts that need volunteers assigned.
    """
    opportunity = Opportunity.objects.get(id=opp_id)
    shifts = []

    # Handle different scheduling modes
    if opportunity.rota_config == "SHARED":
        # Shared scheduling: same dates across all roles
        schedules = OneOffDate.objects.filter(
            opportunity=opportunity,
            date__gte=datetime.now().date(),
            role__isnull=True  # Only get shared schedules
        )
        roles = Role.objects.filter(opportunity=opp_id)

        for schedule in schedules:
            for role in roles:
                sections = Section.objects.filter(role=role.id)
                available_volunteers = get_shift_volunteers(schedule.id, role.id)

                if sections.exists():
                    # Role has sections - create shift for each section
                    for section in sections:
                        shifts.append({
                            'section': section,
                            'role': role,
                            'schedule': schedule,
                            'available_volunteers': available_volunteers,
                            'assigned_volunteers': get_assigned_volunteers(schedule.id, role.id, section.id),
                            'accepted_volunteers': get_accepted_shifts(schedule.id, role.id, section.id),
                        })
                else:
                    # Role has no sections
                    shifts.append({
                        'role': role,
                        'schedule': schedule,
                        'section': None,
                        'available_volunteers': available_volunteers,
                        'assigned_volunteers': get_assigned_volunteers(schedule.id, role.id),
                        'accepted_volunteers': get_accepted_shifts(schedule.id, role.id),
                    })
    else:
        # Per-role scheduling: each role has its own dates
        shifts = get_available_volunteers_discrete(opportunity.id)

    # Check for unconfirmed shifts
    unconfirmed_shifts = VolunteerShift.objects.filter(
        registration__opportunity=opportunity,
        confirmed=False
    ).exists()

    if unconfirmed_shifts:
        print('[Debug]: Found unconfirmed shifts')

    context = {
        'hx': check_if_hx(request),
        'shifts': shifts,
        'opp': opportunity,
        'unconfirmed_shifts': unconfirmed_shifts,
        'success': success,
        'error': error,
    }

    return render(request, "org_admin/rota/shift_assignment.html", context)


def get_assigned_volunteers(schedule_id, role_id, section_id=None):
    """
    Get volunteers who are already assigned to a specific shift.

    Args:
        schedule_id: ID of the schedule/date
        role_id: ID of the role
        section_id: Optional section ID for section-specific assignments

    Returns:
        QuerySet of Registration objects for assigned volunteers
    """
    try:
        role = Role.objects.get(id=role_id)
        schedule = OneOffDate.objects.get(id=schedule_id)

        # Filter registrations for active ones only
        registrations = Registration.objects.filter(opportunity=role.opportunity)
        active_registrations = [r.id for r in registrations if r.get_registration_status() == 'active']

        # Build filter for volunteer shifts
        shift_filter = {
            'registration__in': active_registrations,
            'role': role,
            'occurrence__one_off_date': schedule,
        }

        # Add section filter if specified
        if section_id:
            shift_filter['section_id'] = section_id
        else:
            shift_filter['section__isnull'] = True

        shifts = VolunteerShift.objects.filter(**shift_filter).values_list('registration_id', flat=True)

        if shifts:
            return Registration.objects.filter(id__in=shifts)
        else:
            return Registration.objects.none()

    except Exception as e:
        print(f"[Error]: get_assigned_volunteers failed: {e}")
        return Registration.objects.none()


def get_shift_volunteers(schedule_id, role_id):
    """
    Get volunteers who are available for a specific shift.
    Excludes volunteers with time conflicts, not just any assignment to the occurrence.

    Args:
        schedule_id: ID of the schedule/date
        role_id: ID of the role

    Returns:
        QuerySet of Registration objects for available volunteers
    """
    try:
        role = Role.objects.get(id=role_id)
        schedule = OneOffDate.objects.get(id=schedule_id)

        # Get active registrations for this opportunity
        registrations = Registration.objects.filter(opportunity=role.opportunity)
        active_registrations = [r.id for r in registrations if r.get_registration_status() == 'active']

        # Get volunteers who marked themselves available for this date
        one_off_available_reg_ids = set(
            VolunteerOneOffDateAvailability.objects.filter(
                registration_id__in=active_registrations,
                one_off_date=schedule
            ).values_list('registration_id', flat=True)
        )

        # Get volunteers who expressed interest in this role
        role_interest_reg_ids = set(
            VolunteerRoleIntrest.objects.filter(
                registration_id__in=active_registrations,
                role=role
            ).values_list('registration_id', flat=True)
        )

        # Volunteers must be available for date AND interested in role
        available_registrations = one_off_available_reg_ids.intersection(role_interest_reg_ids)
        print(f"[Debug]: Initially available volunteers: {available_registrations}")

        # Filter out volunteers with time conflicts (not just any assignment)
        if available_registrations:
            conflicted_volunteers = set()

            # Check each volunteer for time conflicts
            for reg_id in available_registrations:
                if check_time_conflict(reg_id, schedule.start_time, schedule.end_time, schedule.date):
                    conflicted_volunteers.add(reg_id)

            # Remove conflicted volunteers
            available_registrations.difference_update(conflicted_volunteers)
            print(f"[Debug]: Available after conflict check: {available_registrations}")

        if available_registrations:
            return Registration.objects.filter(id__in=available_registrations)
        else:
            return Registration.objects.none()

    except Exception as e:
        print(f"[Error]: get_shift_volunteers failed: {e}")
        return Registration.objects.none()


def get_accepted_shifts(schedule_id, role_id, section_id=None):
    """
    Get volunteers who have confirmed and accepted their shift assignments.
    Returns a list with [accepted_volunteers_queryset, confirmed_volunteers_queryset]
    that the template can use with |length filter.

    Args:
        schedule_id: ID of the schedule/date
        role_id: ID of the role
        section_id: Optional section ID for section-specific assignments

    Returns:
        List containing [accepted_volunteers, confirmed_volunteers] as QuerySets
    """
    try:
        role = Role.objects.get(id=role_id)
        schedule = OneOffDate.objects.get(id=schedule_id)

        # Filter for active registrations
        registrations = Registration.objects.filter(opportunity=role.opportunity)
        active_registrations = [r.id for r in registrations if r.get_registration_status() == 'active']

        # Build base filter
        base_filter = {
            'registration__in': active_registrations,
            'role': role,
            'occurrence__one_off_date': schedule,
            'confirmed': True
        }

        # Add section filter
        if section_id:
            base_filter['section_id'] = section_id
        else:
            base_filter['section__isnull'] = True

        # Get confirmed volunteers (returns Registration QuerySet)
        confirmed_shift_ids = VolunteerShift.objects.filter(**base_filter).values_list('registration_id', flat=True)
        confirmed_volunteers = Registration.objects.filter(id__in=confirmed_shift_ids)

        # Get accepted volunteers (confirmed + accepted RSVP)
        accepted_filter = base_filter.copy()
        accepted_filter['rsvp_response'] = 'yes'
        accepted_shift_ids = VolunteerShift.objects.filter(**accepted_filter).values_list('registration_id', flat=True)
        accepted_volunteers = Registration.objects.filter(id__in=accepted_shift_ids)

        return [accepted_volunteers, confirmed_volunteers]

    except Exception as e:
        print(f"[Error]: get_accepted_shifts failed: {e}")
        return [Registration.objects.none(), Registration.objects.none()]


def get_accepted_shifts(schedule_id, role_id, section_id=None):
    """
    Get volunteers who have confirmed and accepted their shift assignments.
    Returns a list with [accepted_volunteers_queryset, confirmed_volunteers_queryset]
    that the template can use with |length filter.

    Args:
        schedule_id: ID of the schedule/date
        role_id: ID of the role
        section_id: Optional section ID for section-specific assignments

    Returns:
        List containing [accepted_volunteers, confirmed_volunteers] as QuerySets
    """
    try:
        role = Role.objects.get(id=role_id)
        schedule = OneOffDate.objects.get(id=schedule_id)

        # Filter for active registrations
        registrations = Registration.objects.filter(opportunity=role.opportunity)
        active_registrations = [r.id for r in registrations if r.get_registration_status() == 'active']

        # Build base filter
        base_filter = {
            'registration__in': active_registrations,
            'role': role,
            'occurrence__one_off_date': schedule,
            'confirmed': True
        }

        # Add section filter
        if section_id:
            base_filter['section_id'] = section_id
        else:
            base_filter['section__isnull'] = True

        # Get confirmed volunteers (returns Registration QuerySet)
        confirmed_shift_ids = VolunteerShift.objects.filter(**base_filter).values_list('registration_id', flat=True)
        confirmed_volunteers = Registration.objects.filter(id__in=confirmed_shift_ids)

        # Get accepted volunteers (confirmed + accepted RSVP)
        accepted_filter = base_filter.copy()
        accepted_filter['rsvp_response'] = 'yes'
        accepted_shift_ids = VolunteerShift.objects.filter(**accepted_filter).values_list('registration_id', flat=True)
        accepted_volunteers = Registration.objects.filter(id__in=accepted_shift_ids)

        return [accepted_volunteers, confirmed_volunteers]

    except Exception as e:
        print(f"[Error]: get_accepted_shifts failed: {e}")
        return [Registration.objects.none(), Registration.objects.none()]


def get_available_volunteers_discrete(opportunity_id):
    """
    Get available volunteers for per-role scheduling mode.
    Each role has its own set of dates.
    """
    roles = Role.objects.filter(opportunity=opportunity_id)
    shifts = []

    for role in roles:
        sections = Section.objects.filter(role=role)
        schedules = OneOffDate.objects.filter(role=role, date__gte=datetime.now().date())

        for schedule in schedules:
            if sections.exists():
                # Role has sections
                for section in sections:
                    shifts.append({
                        'role': role,
                        'schedule': schedule,
                        'available_volunteers': get_shift_volunteers(schedule.id, role.id),
                        'assigned_volunteers': get_assigned_volunteers(schedule.id, role.id, section.id),
                        'accepted_volunteers': get_accepted_shifts(schedule.id, role.id, section.id),
                        'section': section,
                    })
            else:
                # Role has no sections
                shifts.append({
                    'role': role,
                    'schedule': schedule,
                    'available_volunteers': get_shift_volunteers(schedule.id, role.id),
                    'assigned_volunteers': get_assigned_volunteers(schedule.id, role.id),
                    'accepted_volunteers': get_accepted_shifts(schedule.id, role.id),
                    'section': None,
                })

    return shifts


def edit_rota_schedule(request, opp_id=None, schedule_id=None, role_id=None):
    """
    Handle creation and editing of schedule dates.
    """
    opportunity = None
    schedule = None

    print(f'[Debug]: edit_rota_schedule - opp_id: {opp_id}, schedule_id: {schedule_id}, role_id: {role_id}')

    if request.method == "POST":
        if not schedule_id:
            return create_schedule(request, opp_id, role_id)
        else:
            return edit_schedule(request, schedule_id)

    # GET request - show the form
    if opp_id:
        try:
            opportunity = Opportunity.objects.get(id=opp_id)
        except Exception as e:
            print(f"[Error]: Could not get opportunity: {e}")
            opportunity = None

    if schedule_id:
        try:
            schedule = OneOffDate.objects.get(id=schedule_id)
            opportunity = schedule.opportunity
        except Exception as e:
            print(f"[Error]: Could not get schedule: {e}")
            schedule = None

    context = {
        'hx': check_if_hx(request),
        'schedule': schedule,
        'opp': opportunity.id if opportunity else None,
        'role': role_id if role_id else None,
    }

    return render(request, "org_admin/rota/one_off_schedule_editor.html", context)


def create_schedule(request, opp_id, role_id=None):
    """
    Create a new schedule date.
    """
    try:
        opportunity = Opportunity.objects.get(id=opp_id)
        role = Role.objects.get(id=role_id) if role_id else None

        schedule = OneOffDate(
            date=request.POST.get('schedule_date'),
            start_time=request.POST.get('schedule_start_time'),
            end_time=request.POST.get('schedule_end_time'),
            opportunity=opportunity,
            role=role,
        )
        schedule.save()

        print(f"[Info]: Created new schedule {schedule.id}")

        request.method = 'GET'
        if schedule.role:
            return edit_role(request, schedule.role.id)
        else:
            return opportunity_rota_index(request, opp_id)

    except Exception as e:
        print(f"[Error]: Failed to create schedule: {e}")
        return opportunity_rota_index(request, opp_id)


def edit_schedule(request, schedule_id):
    """
    Update an existing schedule date.
    """
    try:
        schedule = OneOffDate.objects.get(id=schedule_id)

        schedule.date = request.POST.get('schedule_date')
        schedule.start_time = request.POST.get('schedule_start_time')
        schedule.end_time = request.POST.get('schedule_end_time')
        schedule.save()

        print(f"[Info]: Updated schedule {schedule.id}")

        request.method = "GET"
        if schedule.role:
            return edit_role(request, schedule.role.id)
        else:
            return opportunity_rota_index(request, schedule.opportunity.id)

    except Exception as e:
        print(f"[Error]: Failed to update schedule: {e}")
        return opportunity_rota_index(request, schedule.opportunity.id if schedule else None)


def rota_index(request):
    """
    Display main rota management page showing all opportunities.
    """
    is_admin = OrganisationAdmin.objects.filter(user=request.user)

    if is_admin.exists():
        organisation = is_admin.first().organisation
        opportunities = Opportunity.objects.filter(organisation=organisation)

        context = {
            'hx': check_if_hx(request),
            'opportunities': opportunities
        }

        return render(request, "org_admin/rota/rota_index.html", context)
    else:
        return render(
            request,
            "org_admin/no_admin.html",
            context={'hx': check_if_hx()}
        )


def edit_section(request, role_id=None, section_id=None):
    """
    Handle creation and editing of role sections.
    """
    section = None
    role = None

    if request.method == "POST":
        if section_id is not None:
            return save_section(request, section_id)
        if role_id is not None:
            return create_new_section(request, role_id)

    # GET request - show the form
    if section_id:
        try:
            section = Section.objects.get(id=section_id)
            role = section.role
        except Exception as e:
            print(f"[Error]: Could not get section: {e}")
            section = None

    if role_id:
        try:
            role = Role.objects.get(id=role_id)
        except Exception as e:
            print(f"[Error]: Could not get role: {e}")
            role = None

    context = {
        'hx': check_if_hx(request),
        'role': role,
        'section': section,
    }

    return render(request, "org_admin/rota/section_editor.html", context)


def save_section(request, section_id):
    """
    Save changes to an existing section.
    """
    try:
        section = Section.objects.get(id=section_id)
        section.name = request.POST.get('section_name', '')
        section.description = request.POST.get('section_description', '')
        section.required_volunteers = int(request.POST.get('section_volunteers', 0))
        section.save()

        print(f"[Info]: Updated section {section.id}")

        request.method = 'GET'
        return edit_role(request, section.role_id)

    except Exception as e:
        print(f"[Error]: Failed to save section: {e}")
        request.method = 'GET'
        return edit_role(request, section.role_id if 'section' in locals() else None)


def create_new_section(request, role_id):
    """
    Create a new section for a role.
    """
    try:
        role = Role.objects.get(id=role_id)

        section = Section(
            name=request.POST.get('section_name', ''),
            description=request.POST.get('section_description', ''),
            required_volunteers=int(request.POST.get('section_volunteers', 0)),
            role=role,
        )
        section.save()

        print(f"[Info]: Created new section {section.id}")

        request.method = 'GET'
        return edit_role(request, role_id)

    except Exception as e:
        print(f"[Error]: Failed to create section: {e}")
        request.method = 'GET'
        return edit_role(request, role_id)


def edit_role(request, role_id=None, opp_id=None):
    """
    Handle creation and editing of volunteer roles.
    """
    role = None
    sections = None
    volunteers_required = None
    one_off_dates = None
    opp = None

    print(f"[Info]: edit_role - method: {request.method}, role_id: {role_id}, opp_id: {opp_id}")

    if request.method == "POST":
        if role_id is not None:
            return save_role(request, role_id)
        if opp_id is not None:
            create_new_rota_role(request, opp_id)
            return opportunity_rota_index(request, opp_id)

    # GET request - show the form
    if role_id:
        try:
            role = Role.objects.get(id=role_id)
            opp = role.opportunity
            sections = Section.objects.filter(role=role)
            volunteers_required = sum(section.required_volunteers for section in sections)
            one_off_dates = OneOffDate.objects.filter(role=role)

        except Exception as e:
            print(f"[Error]: Could not get role: {e}")
            role = None

    elif opp_id:
        try:
            opp = Opportunity.objects.get(id=opp_id)
        except Exception as e:
            print(f"[Error]: Could not get opportunity: {e}")
            opp = None

    context = {
        "hx": check_if_hx(request),
        "opp": opp,
        "role": role,
        "sections": sections,
        "volunteers_required": volunteers_required,
        "one_off_dates": one_off_dates,
    }

    return render(request, "org_admin/rota/role_editor.html", context)


def create_new_rota_role(request, opp_id):
    """
    Create a new volunteer role.
    """
    try:
        opportunity = Opportunity.objects.get(id=opp_id)

        role = Role(
            name=request.POST.get("role_name", ""),
            description=request.POST.get("role_description", ""),
            volunteer_description=request.POST.get("volunteer_description", ""),
            required_volunteers=request.POST.get("role_volunteers", 0),
            opportunity=opportunity,
        )
        role.save()

        print(f"[Info]: Created new role {role.id}")

    except Exception as e:
        print(f"[Error]: Failed to create role: {e}")

    return opportunity_rota_index(request, opp_id)


def save_role(request, role_id):
    """
    Save changes to an existing role.
    """
    try:
        role = Role.objects.get(id=role_id)
        role.name = request.POST.get("role_name", "")
        role.description = request.POST.get("role_description", "")
        role.volunteer_description = request.POST.get("volunteer_description", "")

        # Only update required volunteers if role has no sections
        if Section.objects.filter(role=role).count() == 0:
            role.required_volunteers = request.POST.get("role_volunteers", 0)

        role.save()

        print(f"[Info]: Updated role {role.id}")

        request.method = 'GET'
        return edit_role(request, role.id)

    except Exception as e:
        print(f"[Error]: Failed to save role: {e}")
        request.method = 'GET'
        return edit_role(request, role_id)


def opportunity_rota_index(request, opportunity_id, error=None, success=None):
    """
    Display rota management page for a specific opportunity.
    """
    try:
        opportunity = Opportunity.objects.get(id=opportunity_id)
        schedules = OneOffDate.objects.filter(opportunity=opportunity, role=None)
        roles = Role.objects.filter(opportunity=opportunity)

        context = {
            'opportunity': opportunity,
            'schedules': schedules,
            'roles': roles,
            'error': error,
            'success': success,
            'hx': check_if_hx(request),
        }

        return render(request, "org_admin/rota/rota_opp_index.html", context)

    except Exception as e:
        print(f"[Error]: Could not get opportunity: {e}")
        return render(request, "org_admin/error.html", {'error': str(e)})


def confirm_shifts(request, opp_id):
    """
    Confirm all unconfirmed shifts for an opportunity and notify volunteers.
    """
    try:
        opportunity = Opportunity.objects.get(id=opp_id)
        count = 0

        unconfirmed_shifts = VolunteerShift.objects.filter(
            registration__opportunity=opportunity,
            confirmed=False
        )

        for shift in unconfirmed_shifts:
            shift.confirmed = True
            shift.save()
            count += 1

        print(f"[Info]: Confirmed {count} shifts for opportunity {opportunity.id}")

        return assign_rota(
            request,
            opportunity.id,
            success=f"Sent shifts to {count} volunteers."
        )

    except Exception as e:
        print(f"[Error]: Failed to confirm shifts: {e}")
        return assign_rota(
            request,
            opp_id,
            error="Failed to confirm shifts. Please try again."
        )

def edit_supervisor(request, supervisor_id):
    admin = OrganisationAdmin.objects.filter(user=request.user).first()


    if supervisor_id:
        try:
            sup = Supervisor.objects.get(
                id=supervisor_id
            )

            sup_opps = Supervisor.objects.get(
                id=supervisor_id
            ).supervisor_opportunities.filter().values_list('id', flat=True)

            sup_roles = Supervisor.objects.get(
                id=supervisor_id
            ).supervisor_roles.filter().values_list('id', flat=True)

            sup_shifts = Supervisor.objects.get(
                id=supervisor_id
            ).supervisor_shifts.filter().values_list('id', flat=True)


        except:
            sup = None
            sup_opps = None
            sup_shifts = None
            sup_roles = None

    else:
        sup = None
        sup_opps = None
        sup_shifts = None
        sup_roles = None

    if admin:
        opportunities = Opportunity.objects.filter(organisation=admin.organisation)
    else:
        opportunities = None

    if admin:
        roles = Role.objects.filter(opportunity__organisation=admin.organisation)
    else:
        roles = None

    if admin:
        shifts = Occurrence.objects.filter(
            one_off_date__opportunity__organisation=admin.organisation,
            one_off_date__date__gt=datetime.now().date())
    else:
        shifts = None



    context = {
        'sup' : sup,
        'hx' : check_if_hx(request),
        'sup_roles' : sup_roles,
        'sup_shifts' : sup_shifts,
        'sup_opps' : sup_opps,
        'roles' : roles,
        'shifts' : shifts,
        'opportunities' : opportunities
    }

    return render(request, "org_admin/rota/add_edit_supervisor.html", context)


def add_supervisor(request):

    if request.method == 'POST':
        return save_supervisor(request)

    context = {
        'hx' : check_if_hx(request)
    }

    return render(request, "org_admin/rota/add_edit_supervisor.html", context)


def partial_opp_picker(request, supervisor_id=None):
    admin = OrganisationAdmin.objects.filter(user=request.user).first()

    if supervisor_id:
        try:
            sup_opps = Supervisor.objects.get(
                id=supervisor_id
            ).supervisor_opportunities.filter().values_list('id', flat=True)
        except:
            sup_opps = None
    else:
        sup_opps = None


    if admin:
        opportunities = Opportunity.objects.filter(organisation=admin.organisation)
    else:
        opportunities = None

    context = {
        'hx' : check_if_hx(request),
        'opportunities' : opportunities,
        'sup_opps' : sup_opps
    }

    return render(request, "org_admin/rota/partials/opp_picker.html", context)

def partial_role_picker(request, supervisor_id=None):
    if supervisor_id:
        try:
            sup_roles = Supervisor.objects.get(
                id=supervisor_id
            ).supervisor_roles.filter().values_list('id', flat=True)
        except:
            sup_roles = None
    else:
        sup_roles = None

    admin = OrganisationAdmin.objects.filter(user=request.user).first()
    if admin:
        roles = Role.objects.filter(opportunity__organisation=admin.organisation)
    else:
        roles = None

    context = {
        'hx' : check_if_hx(request),
        'roles' : roles,
        'sup_roles' : sup_roles
    }

    return render(request, "org_admin/rota/partials/role_picker.html", context)

def partial_shift_picker(request, supervisor_id=None):
    if supervisor_id:
        try:
            sup_shifts = Supervisor.objects.get(
                id=supervisor_id
            ).supervisor_shifts.filter().values_list('id', flat=True)
        except:
            sup_shifts = None
    else:
        sup_shifts = None

    admin = OrganisationAdmin.objects.filter(user=request.user).first()
    if admin:
        shifts = Occurrence.objects.filter(
            one_off_date__opportunity__organisation=admin.organisation,
            one_off_date__date__gt=datetime.now().date())
    else:
        shifts = None

    context = {
        'shifts' : shifts,
        'hx' : check_if_hx(request),
        'sup_shifts' : sup_shifts
    }

    return render(request, "org_admin/rota/partials/shift_picker.html", context)


def save_supervisor(request, supervisor_id=None):
    data = request.POST
    admin = OrganisationAdmin.objects.filter(user=request.user).first()
    supervisor = Supervisor.objects.get(id=supervisor_id) if supervisor_id else None

    print(data)

    if not supervisor_id:
        email = request.POST['sup_email']

        if not email or len(email) == 0:
            return supervisor_index(request, error="Enter valid email!")

        user = User.objects.filter(email=email)
        if user.exists():
            # Check that an existing profile for this supervisor doesn't already exist
            sup = Supervisor.objects.filter(
                organisation = admin.organisation,
                user = user.first()
            )

            if sup.exists():
                return supervisor_index(request, error="User already exists as a supervisor")
            else:
                supervisor = Supervisor(
                    user=user.first(),
                    organisation=admin.organisation,
                )

                supervisor.save()
        else:
            user = User.objects.create_user(
                email=email,
                username=email
            )
            user.set_unusable_password()
            user.save()



            supervisor = Supervisor(
                user=user,
                organisation=admin.organisation,
            )

            supervisor.save()


    #At this point we should have a supervisor

    if supervisor:
        access_level = request.POST['access_type']

        print(access_level, type(access_level))

        match access_level:
            case 'all_org':
                print('[debug] Matched all_org')
                supervisor.access_level = 'all_org'
            case 'opp':
                print('[debug] Matched opp')
                supervisor.access_level = 'all_opportunity'
                supervisor.supervisor_opportunities.set(
                    Opportunity.objects.filter(
                        id__in=request.POST.getlist('opp_select')
                    )
                )
            case 'roles':
                print('[debug] Matched roles')
                supervisor.access_level = 'all_role'
                supervisor.supervisor_roles.set(
                    Role.objects.filter(
                        id__in=request.POST.getlist('role_select')
                    )
                )
            case 'shifts':
                print('[debug] Matched shifts')
                supervisor.access_level = 'specific_shifts'
                supervisor.supervisor_shifts.set(
                    Role.objects.filter(
                        id__in=request.POST.getlist('shift_select')
                    )
                )
        supervisor.save()


    return supervisor_index(request)

