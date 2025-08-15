from datetime import datetime
from logging import exception

from django.shortcuts import render

from organisations.models import Organisation
from commonui.views import check_if_hx
from opportunities.models import Opportunity, Registration
from org_admin.models import OrganisationAdmin
from rota.models import Role, Section, VolunteerShift, OneOffDate, VolunteerOneOffDateAvailability, \
    VolunteerRoleIntrest, Occurrence, Supervisor

def supervisor_index(request):
    is_admin = OrganisationAdmin.objects.filter(user=request.user)

    if is_admin.exists():
        organisation = is_admin.first().organisation

        supervisors = Supervisor.objects.filter(
            organisation = organisation
        )

        context = {
            "organisation" : organisation,
            'hx' : check_if_hx(request),
            'supervisors' : supervisors
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
            context={'hx':check_if_hx()}
        )

def toggle_opportunity_scheduling_type(request, opportunity_id):
    opportunity = Opportunity.objects.get(id = opportunity_id)

    if opportunity.rota_config == "SHARED":
        opportunity.rota_config = "PER_ROLE"
    elif opportunity.rota_config == "PER_ROLE":
        opportunity.rota_config = "SHARED"

    opportunity.save()

    return opportunity_rota_index(request, opportunity_id)

def unassign_volunteer_shift_instance(request, registration_id, role_id):
    try:
        shift = VolunteerShift.objects.filter(registration_id=registration_id, role_id=role_id).first()
        role_id = shift.role.id
        schedule_id = shift.occurrence.one_off_date.id
        section_id = shift.section.id if shift.section else None
        shift.delete()
        return assign_volunteer_shift(request, role_id, schedule_id, section_id)
    except Exception as e:
        print("[Error]: ", e)

def assign_volunteer_shift_instance(request, registration_id, role_id, schedule_id, section_id=None):
    print("[info]: Got section id:", section_id)

    assigned_shifts = None
    opportunity = None
    role = None
    schedule = None
    registration = None
    section = None
    try:
        role = Role.objects.get(id=role_id)
        schedule = OneOffDate.objects.get(id=schedule_id)
        registration = Registration.objects.get(id=registration_id)
        section = Section.objects.get(id=section_id) if section_id else None
        opportunity = role.opportunity
    except Exception as e:
        print("[Error]: ", e)

    volunteer_registrations = get_shift_volunteers(schedule.id, role.id)

    if registration_id not in volunteer_registrations.values_list('id', flat=True):
        return "errrrror"

    # check if an occurance aleader

    occurrence = Occurrence.objects.filter(
        one_off_date=schedule,
    )

    if occurrence.exists():
        occurrence = occurrence[0]
    else:
        occurrence = Occurrence(
            one_off_date=schedule,
            date=schedule.date,
            start_time=schedule.start_time,
            end_time=schedule.end_time,
        )

        occurrence.save()

    shift = VolunteerShift.objects.create(
        registration=registration,
        occurrence=occurrence,
        role=role,
        section=section,
    )

    shift.save()

    return assign_volunteer_shift(request, role_id, schedule_id, section_id)

def assign_volunteer_shift(request, role_id, schedule_id, section_id=None):
    print("[Debug]: assign_volunteer_shift")
    assigned_shifts = None
    opportunity = None
    role = None
    schedule = None

    try:
        role = Role.objects.get(id=role_id)
        schedule = OneOffDate.objects.get(id=schedule_id)
        opportunity = role.opportunity
    except Exception as e:
        print("[Error]: ", e)

    volunteer_registrations = get_shift_volunteers(schedule.id, role.id)
    assigned_volunteers = get_assigned_volunteers(schedule.id, role.id, section_id)

    context = {
        'hx': check_if_hx(request),
        'opp': opportunity,
        'registrations': volunteer_registrations,
        'assigned_volunteers': assigned_volunteers,
        'schedule_id': schedule.id,
        'section_id': section_id,
        'role_id': role.id,

    }

    return render(request, 'org_admin/rota/volunteer_shift_assignment.html', context)

def assign_rota(request, opp_id, success=None, error=None):
    opportunity = Opportunity.objects.get(id=opp_id)
    shifts = []

    if opportunity.rota_config == "SHARED":
        schedules = OneOffDate.objects.filter(opportunity=opportunity, date__gte=datetime.now())
        roles = Role.objects.filter(opportunity=opp_id)

        for schedule in schedules:
            for role in roles:
                sections = Section.objects.filter(role=role.id)
                available_volunteers = get_shift_volunteers(schedule.id, role.id)

                if sections.count() > 0:
                    for section in sections:
                        shifts.append({
                            'section': section,
                            'role': role,
                            'schedule': schedule,
                            'available_volunteers': available_volunteers,
                            'assigned_volunteers': get_assigned_volunteers(schedule.id, role.id, section.id),
                        })
                else:
                    shifts.append({
                        'role': role,
                        'schedule': schedule,
                        'section': None,
                        'available_volunteers': available_volunteers,
                        'assigned_volunteers': get_assigned_volunteers(schedule.id, role.id),
                    })
    else:
        shifts = get_available_volunteers_discrete(opportunity.id)

    unconfirmed_shifts = False

    if VolunteerShift.objects.filter(
        registration__opportunity = opportunity,
        confirmed=False
    ).exists():
        print('[Debug] found unconfirmed shifts')
        unconfirmed_shifts = True


    context = {
        'hx': check_if_hx(request),
        'shifts': shifts,
        'opp': opportunity,
        'unconfirmed_shifts' : unconfirmed_shifts,
        'success' : success,
        'error' : error,
    }

    return render(request, "org_admin/rota/shift_assignment.html", context)

def get_assigned_volunteers(schedule_id, role_id, section_id=None):
    role = Role.objects.get(id=role_id)
    schedule = OneOffDate.objects.get(id=schedule_id)

    # Filter registrations for the given opportunity that are active.
    registrations = Registration.objects.filter(opportunity=role.opportunity)
    active_registrations = [r.id for r in registrations if r.get_registration_status() == 'active']

    if not section_id:
        shifts = VolunteerShift.objects.filter(
            registration__in=active_registrations,
            role=role,
            occurrence__one_off_date=schedule,

        ).values_list('registration_id', flat=True)
    else:
        print("[Info]: ", schedule_id)
        shifts = VolunteerShift.objects.filter(
            registration__in=active_registrations,
            role=role,
            occurrence__one_off_date=schedule,
            section_id=section_id,

        ).values_list('registration_id', flat=True)

    if shifts != None:
        # Return queryset of Registration objects for these IDs:
        return Registration.objects.filter(id__in=shifts)
    else:
        return None

def get_shift_volunteers(schedule_id, role_id):
    role = Role.objects.get(id=role_id)
    schedule = OneOffDate.objects.get(id=schedule_id)

    # Filter registrations for the given opportunity that are active.
    registrations = Registration.objects.filter(opportunity=role.opportunity)

    # Ideally filter active registrations in DB if possible;
    # otherwise your current approach:
    active_registrations = [r.id for r in registrations if r.get_registration_status() == 'active']

    # Filter VolunteerOneOffDateAvailability by registration and one_off_date
    one_off_reg_ids = set(
        VolunteerOneOffDateAvailability.objects.filter(
            registration_id__in=active_registrations,
            one_off_date=schedule
        ).values_list('registration_id', flat=True))

    # Filter VolunteerRoleIntrest by registration and role
    role_intrest_reg_ids = set(
        VolunteerRoleIntrest.objects.filter(
            registration_id__in=active_registrations,
            role=role
        ).values_list('registration_id', flat=True))

    registrations_in_both = one_off_reg_ids.intersection(role_intrest_reg_ids)
    print("[Debug]: registrations_in_both: ", registrations_in_both)
    # Check if a one-off_occurrence exists

    if Occurrence.objects.filter(one_off_date=schedule).exists():
        occurrence = Occurrence.objects.get(one_off_date=schedule)

        # Filter out if shifts have been assigned
        assigned_shift_volunteers = set(VolunteerShift.objects.filter(
            registration__opportunity=role.opportunity,
            occurrence=occurrence,
        ).values_list('registration_id', flat=True))

        registrations_in_both.difference_update(assigned_shift_volunteers)
        print("[Debug]: registrations_in_both 2: ", registrations_in_both)

    if registrations_in_both != None:

        # Return queryset of Registration objects for these IDs:
        return Registration.objects.filter(id__in=registrations_in_both)
    else:
        return None

def get_accepted_shifts(schedule_id, role_id, section_id=None):
    role = Role.objects.get(id=role_id)
    schedule = OneOffDate.objects.get(id=schedule_id)

    # Filter registrations for the given opportunity that are active.
    registrations = Registration.objects.filter(opportunity=role.opportunity)
    active_registrations = [r.id for r in registrations if r.get_registration_status() == 'active']

    if not section_id:
        shifts_confirmed = VolunteerShift.objects.filter(
            registration__in=active_registrations,
            role=role,
            occurrence__one_off_date=schedule,
            confirmed=True
        ).values_list('registration_id', flat=True)

        shifts_accepted = VolunteerShift.objects.filter(
            registration__in=active_registrations,
            role=role,
            occurrence__one_off_date=schedule,
            confirmed=True,
            rsvp_response='yes'
        ).values_list('registration_id', flat=True)

    else:
        print("[Info]: ", schedule_id)
        shifts_confirmed = VolunteerShift.objects.filter(
            registration__in=active_registrations,
            role=role,
            occurrence__one_off_date=schedule,
            section_id=section_id,
            confirmed=True
        ).values_list('registration_id', flat=True)

        shifts_accepted = VolunteerShift.objects.filter(
            registration__in=active_registrations,
            role=role,
            occurrence__one_off_date=schedule,
            section_id=section_id,
            confirmed=True,
            rsvp_response = 'yes'
        ).values_list('registration_id', flat=True)

    return [shifts_accepted, shifts_confirmed]

def get_available_volunteers_discrete(opportunity_id):
    roles = Role.objects.filter(opportunity=opportunity_id)

    shifts = []

    for role in roles:
        sections = Section.objects.filter(role=role)
        schedules = OneOffDate.objects.filter(role=role)
        for schedule in schedules:

            if sections.count() > 0:
                for section in sections:

                    shifts.append({
                        'role': role,
                        'schedule': schedule,
                        'available_volunteers': get_shift_volunteers(schedule.id, role.id),
                        'assigned_volunteers': get_assigned_volunteers(schedule.id, role.id, section.id),
                        'accepted_volunteers' : get_accepted_shifts(schedule.id, role.id, section.id),
                        'section': section,
                    })
            else:
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
    opportunity = None
    schedule = None

    print('[Debug] new schedule', opp_id, schedule_id, role_id)

    if request.method == "POST":
        if not schedule_id:
            return create_schedule(request, opp_id, role_id)
        else:
            return edit_schedule(request, schedule_id)

    if opp_id:
        try:
            opportunity = Opportunity.objects.get(id=opp_id)
        except Exception as e:
            print("got ooops", e)
            opportunity = None

    if schedule_id:
        try:
            print("got sched")
            schedule = OneOffDate.objects.get(id=schedule_id)
            opportunity = schedule.opportunity
        except Exception as e:
            print("got ooops", e)
            schedule = None

    context = {
        'hx': check_if_hx(request),
        'schedule': schedule,
        'opp': opportunity.id if opportunity else None,
        'role': role_id if role_id else None,
    }

    return render(request, "org_admin/rota/one_off_schedule_editor.html", context)

def create_schedule(request, opp_id, role_id=None):
    role = None
    opportunity = Opportunity.objects.get(id=opp_id)

    try:
        if role_id != None:
            role = Role.objects.get(id=role_id)
    except Exception as e:
        print("[Error]: ", e, role_id)

    print("[Info]: ", role)

    schedule = OneOffDate(
        date=request.POST.get('schedule_date'),
        start_time=request.POST.get('schedule_start_time'),
        end_time=request.POST.get('schedule_end_time'),
        opportunity=opportunity,
        role = role,
    )

    schedule.save()

    request.method = 'GET'

    if schedule.role != None:
        return edit_role(request, schedule.role.id)
    else:
        return opportunity_rota_index(request, opp_id)

def edit_schedule(request, schedule_id):
    schedule = OneOffDate.objects.get(id=schedule_id)
    date = request.POST.get('schedule_date')
    start_time = request.POST.get('schedule_start_time')
    end_time = request.POST.get('schedule_end_time')

    schedule.date = date
    schedule.start_time = start_time
    schedule.end_time = end_time

    schedule.save()

    request.method = "GET"

    if schedule.role != None:
        return edit_role(request, schedule.role.id)
    else:
        return opportunity_rota_index(request, schedule.opportunity.id)

def rota_index(request):
    is_admin = OrganisationAdmin.objects.filter(user=request.user)

    if is_admin.exists():
        organisation = is_admin.first().organisation

        opportunities = Opportunity.objects.filter(organisation=organisation)

        context = {
            'hx': check_if_hx(request),
            'opportunities' : opportunities
        }

        return render(request, "org_admin/rota/rota_index.html", context)

    else:
        return render(
            request,
            "org_admin/no_admin.html",
            context={'hx': check_if_hx()}
        )

def edit_section(request, role_id=None, section_id=None):
    section = None
    role = None

    if request.method == "POST":
        if section_id is not None:
            print("editing section")
            return save_section(request, section_id)

        if role_id is not None:
            return create_new_section(request, role_id)

    if section_id:
        try:
            section = Section.objects.get(id=section_id)
            role = section.role
        except:
            section = None

    if role_id:
        try:
            role = Role.objects.get(id=role_id)
        except:
            role = None

    context = {
        'hx': check_if_hx(request),
        'role': role,
        'section': section,
    }

    return render(request, "org_admin/rota/section_editor.html", context)

def save_section(request, section_id):
    try:
        section = Section.objects.get(id=section_id)
        section.name = request.POST['section_name']
        section.description = request.POST['section_description']
        section.required_volunteers = int(request.POST['section_volunteers'])
        section.save()
        request.method = 'GET'
        return edit_role(request, section.role_id)
    except:
        request.method = 'GET'
        return edit_role(request, section.role_id)

def create_new_section(request, role_id):
    role = Role.objects.get(id=role_id)
    section = Section(
        name=request.POST['section_name'],
        description=request.POST['section_description'],
        required_volunteers=int(request.POST['section_volunteers']),
        role=role,
    )
    section.save()

    request.method = 'GET'
    return edit_role(request, role_id)

def edit_role(request, role_id=None, opp_id=None):
    role = None
    opp_id = opp_id
    sections = None
    volunteers_required = None
    one_off_dates = None
    opp=None

    print("[Info]: ", request.method)

    if request.method == "POST":
        if role_id is not None:
            return save_role(request, role_id)

        if opp_id is not None:
            create_new_rota_role(request, opp_id)
            return opportunity_rota_index(request, opp_id)

    if role_id:
        try:
            role = Role.objects.get(id=role_id)
            opp = role.opportunity
            sections = Section.objects.filter(role=role)
            volunteers_required = sum(section.required_volunteers for section in sections)
            one_off_dates = OneOffDate.objects.filter(
                role=role
            )

        except Exception as e:
            role = None
            print("[Error]: ", e)
    elif opp_id:
        opp = Opportunity.objects.get(
            id=opp_id
        )


    print("[Info]: ", role)
    print("[Info]: ", one_off_dates)
    print("[Info]: ", opp, role_id, opp_id)


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
    opportunity = Opportunity.objects.get(id=opp_id)

    role = Role(
        name=request.POST["role_name"],
        description=request.POST["role_description"],
        volunteer_description=request.POST["volunteer_description"],
        required_volunteers=request.POST["role_volunteers"],
        opportunity=opportunity,
    )

    role.save()

    return opportunity_rota_index(request, opp_id)

def save_role(request, role_id=None):
    role = Role.objects.get(id=role_id)
    role.name = request.POST["role_name"]
    role.description = request.POST["role_description"]
    role.volunteer_description = request.POST["volunteer_description"]

    if Section.objects.filter(role=role).count() == 0:
        role.required_volunteers = request.POST["role_volunteers"]

    role.save()

    request.method = 'GET'
    return edit_role(request, role.id)

def opportunity_rota_index(request, opportunity_id, error=None, success=None):
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

def confirm_shifts(request, opp_id):
    opportunity = Opportunity.objects.filter(id=opp_id)

    count = 0

    if opportunity.exists():
        opportunity = opportunity.first()
        unconfirmed_shifts = VolunteerShift.objects.filter(
            registration__opportunity = opportunity,
            confirmed=False
        )

        for shift in unconfirmed_shifts:
            shift.confirmed = True
            shift.save()
            count += 1

        return assign_rota(request, opportunity.id, success=f"Sent shifts to {count} volunteers.")
