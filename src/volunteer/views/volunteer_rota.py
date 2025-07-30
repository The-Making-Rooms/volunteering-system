from datetime import datetime
from django.shortcuts import render
from opportunities.models import Registration
from rota.models import VolunteerRoleIntrest, VolunteerOneOffDateAvailability, OneOffDate, Role, VolunteerShift
from commonui.views import check_if_hx

def manage_registration_preferences(request, registration_id):
    registration = Registration.objects.get(id=registration_id)

    if registration.volunteer.user != request.user:
        return render(request, "404.html", context={"hx": check_if_hx(request)})

    if registration.get_registration_status() != 'active':
        return render(request, "404.html", context={"hx": check_if_hx(request)})

    if request.method == "POST":
        update_registration_preferences(request, registration_id)

    opportunity = registration.opportunity
    dates = OneOffDate.objects.filter(opportunity=opportunity, date__gte=datetime.now())
    roles = Role.objects.filter(opportunity=opportunity)

    volunteer_dates = list(VolunteerOneOffDateAvailability.objects.filter(registration=registration).values_list('one_off_date_id', flat=True))
    volunteer_roles = list(VolunteerRoleIntrest.objects.filter(registration=registration).values_list('role_id', flat=True))

    context = {
        'hx' : check_if_hx(request),
        'registration': registration,
        'opportunity': opportunity,
        'dates': dates,
        'roles': roles,
        'volunteer_dates': volunteer_dates,
        'volunteer_roles': volunteer_roles,
    }

    return render(request, "volunteer/manage_registration_preferences.html", context)

def update_registration_preferences(request, registration_id):
    registration = Registration.objects.get(id=registration_id)

    if registration.volunteer.user != request.user:
        return render(request, "404.html")

    if registration.get_registration_status() != 'active':
        return render(request, "404.html")

    updated_dates = [key.split("_")[1] for key in request.POST.keys() if key.startswith('schedule_')]
    updated_roles = [key.split("_")[1] for key in request.POST.keys() if key.startswith('roles_')]

    #Delete any dates not in the reply:

    current_dates = VolunteerOneOffDateAvailability.objects.filter(registration=registration)
    current_roles = VolunteerRoleIntrest.objects.filter(registration=registration)

    print(updated_dates, updated_roles)

    for date in current_dates:
        if date.id not in updated_dates:
            date.delete()
        else:
            updated_dates.remove(date.id)

    for role in current_roles:
        if role not in updated_roles:
            role.delete()
        else:
            updated_roles.remove(role.id)

    #create remaining dates and roles
    print(updated_dates, updated_roles)

    for date in updated_dates:
        new_date = VolunteerOneOffDateAvailability(
            registration=registration,
            one_off_date=OneOffDate.objects.get(id=date),
        )
        new_date.save()

    for role in updated_roles:
        new_role = VolunteerRoleIntrest(
            registration=registration,
            role=Role.objects.get(id=role),
        )
        new_role.save()


    request.method = 'GET'

    return manage_registration_preferences(request, registration_id)

def manage_registration_shifts(request, registration_id):

    registration = Registration.objects.get(id=registration_id)

    if registration.volunteer.user != request.user:
        return render(request, "404.html", context={"hx": check_if_hx(request)})

    if registration.get_registration_status() != 'active':
        return render(request, "404.html", context={"hx": check_if_hx(request)})

    shifts = VolunteerShift.objects.filter(registration=registration)

    context = {
        'hx' : check_if_hx(request),
        'shifts': shifts,
    }

    return render(request, "volunteer/registration_shifts.html", context)