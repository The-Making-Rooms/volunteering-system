#volunteer/views/volunteer_rota.py

from datetime import datetime
from django.utils import timezone
from django.shortcuts import render
from opportunities.models import Registration
from rota.models import VolunteerRoleIntrest, VolunteerOneOffDateAvailability, OneOffDate, Role, VolunteerShift
from commonui.views import check_if_hx, HTTPResponseHXRedirect
from django.core.mail import send_mail
from threading import Thread
from typing import List

def get_deduplicated_dates(request):
    roles = [key.split("_")[1] for key in request.POST.keys() if key.startswith('roles_')]

    dates = []

    for role_sub in roles:
        try:
            role = Role.objects.get(id=role_sub)

            one_off_dates = VolunteerOneOffDateAvailability.objects.filter(
                role=role,
            )

            # Extract date, start_time, end_time from each instance
            for availability in one_off_dates:
                date_tuple = (
                    availability.date,
                    availability.start_time,
                    availability.end_time
                )
                dates.append(date_tuple)

        except Role.DoesNotExist:
            # More specific exception handling
            continue
        except Exception:
            # Handle other potential exceptions
            continue

    # Remove duplicates by converting to set and back to list
    deduplicated_dates = list(set(dates))

    return deduplicated_dates


def manage_registration_preferences(request, registration_id):
    registration = Registration.objects.get(id=registration_id)

    if registration.volunteer.user != request.user:
        return render(request, "404.html", context={"hx": check_if_hx(request)})

    if registration.get_registration_status() != 'active':
        return render(request, "404.html", context={"hx": check_if_hx(request)})

    if request.method == "POST":
        print(request.POST)



        update_registration_preferences(request, registration_id)

    opportunity = registration.opportunity
    roles = Role.objects.filter(opportunity=opportunity)

    volunteer_dates = list(VolunteerOneOffDateAvailability.objects.filter(registration=registration).values_list('one_off_date_id', flat=True))
    volunteer_roles = list(VolunteerRoleIntrest.objects.filter(registration=registration).values_list('role_id', flat=True))


    if opportunity.rota_config == "SHARED":
        # Fetch all future OneOffDates for this opportunity (including role-specific and shared)
        dates_qs = OneOffDate.objects.filter(
            opportunity=opportunity,
            date__gte=timezone.now().date()
        ).order_by('date', 'start_time')

    else:
        dates_qs = OneOffDate.objects.filter(
            role_id__in=volunteer_roles,
            date__gte=timezone.now().date()
        ).order_by('date', 'start_time')


    # Deduplicate into template-friendly structure
    seen = {}
    for date_obj in dates_qs:
        key = (date_obj.date, date_obj.start_time, date_obj.end_time)
        if key not in seen:
            seen[key] = {
                'date': date_obj.date,
                'start_time': date_obj.start_time,
                'end_time': date_obj.end_time,
                'ids': [date_obj.id],
                'is_checked' : set(volunteer_dates).issubset({date_obj.id})
            }
        else:
            if date_obj.id not in seen[key]['ids']:
                seen[key]['ids'].append(date_obj.id)
                print(set(seen[key]['ids']))
                seen[key]['is_checked']: len(set(volunteer_dates).intersection(set(seen[key]['ids']))) > 0

    available_dates = list(seen.values())

    print(available_dates)
    print(volunteer_roles, volunteer_dates)

    context = {
        'hx' : check_if_hx(request),
        'registration': registration,
        'opportunity': opportunity,
        'dates': available_dates,
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

    shifts = VolunteerShift.objects.filter(registration=registration, rsvp_response__in=['-','yes'])

    context = {
        'hx' : check_if_hx(request),
        'registration' : registration,
        'shifts': shifts,
    }

    return render(request, "volunteer/registration_shifts.html", context)


def accept_shift_rsvp(request, shift_id):
    shift = VolunteerShift.objects.get(id=shift_id)

    if shift.registration.volunteer.user != request.user:
        return render(request, "404.html", context={"hx": check_if_hx(request)})

    else:
        shift.rsvp_response = 'yes'
        shift.save()
        return manage_registration_shifts(request, shift.registration.id)


def decline_shift_rsvp(request, shift_id, response):
    shift = VolunteerShift.objects.get(id=shift_id)
    if shift.registration.volunteer.user != request.user:
        print('[error]: user issue')
        return render(request, "404.html", context={"hx": check_if_hx(request)})

    if response != 'cmi' and response != 'decline':
        print('[error]: got response', response)
        return render(request, "404.html", context={"hx": check_if_hx(request)})

    if request.method == "POST":
        match response:
            case "cmi":
                shift.rsvp_response = "cmi"
            case "decline":
                shift.rsvp_response = "decline"

        shift.rsvp_reason = request.POST['reason']

        shift.save()
        request.method='GET'

        return HTTPResponseHXRedirect('/volunteer/your-opportunities/')

    else:

        context = {
            'hx' : check_if_hx(request),
            'shift' : shift,
            'rsvp_reason' : response,
            'modal_title_text': "Cant make it?" if response == "cmi" else "Decline shift"
        }

        return render(request, "volunteer/partials/rsvp_reason_modal.html", context)


def send_confirmation_email_thread(recipients: List[str], subject, message):
    send_mail(
        subject,
        message,
        None,
        recipients,
        fail_silently=True,
    )