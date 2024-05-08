from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from volunteer.models import (
    Volunteer,
    VolunteerAddress,
    EmergencyContacts,
    VolunteerConditions,
)
from opportunities.models import Registration, VolunteerRegistrationStatus, RegistrationAbsence, RegistrationStatus
from django.core.exceptions import ObjectDoesNotExist
import random
from django.contrib.auth.decorators import login_required
from commonui.views import check_if_hx, HTTPResponseHXRedirect
from datetime import datetime
from django.contrib.auth.models import User
from django.contrib.auth import logout
from .forms import (
    VolunteerForm,
    VolunteerAddressForm,
    EmergencyContactsForm,
    VolunteerConditionsForm,
)

# Create your views here.
def check_valid_origin(func, expected_url_end, redirect_path):
    def inner(request):
        match request.method:
            case "GET":
                try:
                    validPath = (
                        request.headers["HX-Current-URL"].split("/")[-2]
                        == expected_url_end
                    )
                except KeyError:
                    return HttpResponseRedirect(redirect_path)
                if validPath:
                    func()
                else:
                    return HttpResponseRedirect(redirect_path)
        return inner()


def index(request):
    if request.user.is_authenticated:
        current_user = request.user
        try:
            volunteer_profile = Volunteer.objects.get(user=current_user)
            print(volunteer_profile)

            context = {
                "hx": check_if_hx(request),
                "volunteer": volunteer_profile,
                "user": current_user,
                "emergency_contacts": EmergencyContacts.objects.filter(
                    volunteer=volunteer_profile
                ),
                "addresses": VolunteerAddress.objects.filter(
                    volunteer=volunteer_profile
                ),
                "conditions": VolunteerConditions.objects.filter(
                    volunteer=volunteer_profile
                ),
                "link_active": "volunteer",
            }

            return render(request, "volunteer/index.html", context=context)

        except ObjectDoesNotExist:
            return render(
                request, "volunteer/container.html", {"hx": check_if_hx(request)}
            )
        except Exception as e:
            print(e)

    else:
        return render(
            request, "commonui/not_logged_in.html", {"hx": check_if_hx(request)}
        )
    
def notify_absence(request, id):
    if request.user.is_authenticated:
        current_user = request.user
        volunteer_profile = Volunteer.objects.get(user=current_user)
        registration = Registration.objects.get(id=id)
        
        if registration.volunteer == volunteer_profile:
            absence = RegistrationAbsence(registration=registration)
            absence.save()
            return HTTPResponseHXRedirect("/volunteer/your-opportunities")
            
                
def stop_volunteering(request, id):
    if request.user.is_authenticated:
        if request.method == "POST":
            current_user = request.user
            if request.POST["submitValue"] != "Yes":
                return HTTPResponseHXRedirect("/volunteer/your-opportunities")
            registration = Registration.objects.get(id=id)
            if registration.volunteer.user != current_user:
                return HTTPResponseHXRedirect("/volunteer/your-opportunities")
            
            try:
                stopped_status = RegistrationStatus.objects.get(status="stopped")
            except ObjectDoesNotExist:
                stopped_status = RegistrationStatus(status="stopped")
                stopped_status.save()
            
            stopped_vol_status = VolunteerRegistrationStatus(registration=registration, registration_status=stopped_status, date=datetime.now())
            stopped_vol_status.save()
            return HTTPResponseHXRedirect("/volunteer/your-opportunities")
        else:
            current_user = request.user
            volunteer_profile = Volunteer.objects.get(user=current_user)
            registration = Registration.objects.get(id=id)
            context = {
                "hx": check_if_hx(request),
                "volunteer": volunteer_profile,
                "registration": registration,
                "link_active": "your-opportunities",
            }
            return render(request, "volunteer/partials/stop_volunteering.html", context=context)

def your_opportunities(request):
    if request.user.is_authenticated == False:
        return render(
            request, "commonui/not_logged_in.html", {"hx": check_if_hx(request)}
        )

    elif Volunteer.objects.filter(user=request.user).exists() != True:
            return render(
                request, "volunteer/container.html", {"hx": check_if_hx(request)}
            )
    else:
    

            volunteer_profile = Volunteer.objects.get(user=request.user)
            registrations = Registration.objects.filter(volunteer=volunteer_profile)
            
            
            data = []
            for registration in registrations:
                print(registration)
                print(VolunteerRegistrationStatus.objects.filter(registration=registration).order_by("-date").first().registration_status.status)
                if VolunteerRegistrationStatus.objects.filter(registration=registration).order_by("-date").first().registration_status.status == "stopped":
                    continue
                is_absent = False
                try:
                    occourance = registration.opportunity.recurrences
                    occourances = occourance.occurrences()
                    print(occourance.dtstart, occourance.dtend, occourance.rrules, list(occourances))
                    last_occurence = occourance.before(datetime.now())
                    next_occurence = occourance.after(datetime.now())
                    
                    print ("Last:",last_occurence)
                    
                    print ("Next", next_occurence)
                    if last_occurence == None:
                        last_occurence = datetime.now()
                    
                    if next_occurence == None:
                        is_absent = False
                    
                    elif RegistrationAbsence.objects.filter(registration=registration, date__gte=last_occurence, date__lte=next_occurence).exists():
                        is_absent = True
                except ValueError:
                    next_occurence = registration.opportunity.recurrences.after(datetime.now())
                    if RegistrationAbsence.objects.filter(registration=registration, date__lte=next_occurence).exists():
                        is_absent = True
                except:
                    next_occurence = None
                    
                        
                print(is_absent)
                
                
                registration_data = {
                    "registration": registration,
                    "status": VolunteerRegistrationStatus.objects.filter(registration=registration).order_by("-date").first(),
                    "next_occurance": next_occurence,
                    "absent": is_absent,
                }
                data.append(registration_data)

            context = {
                "hx": check_if_hx(request),
                "volunteer": volunteer_profile,
                "user": request.user,
                "data": data,
                "link_active": "your-opportunities",
            }
            return render(request, "volunteer/your_opportunities.html", context=context)

def get_volunteer_if_exists(user):
    try:
        volunteer_profile = Volunteer.objects.get(user=user)
        return volunteer_profile
    except ObjectDoesNotExist:
        return None

def volunteer_form(request):
    if request.method == "GET":
        context = {
            "hx": check_if_hx(request),
            "volunteer": get_volunteer_if_exists(request.user),
        }
        return render(
            request, "volunteer/partials/volunteer_form.html", context=context
        )

    elif request.method == "POST":
        data = request.POST
        user = User.objects.get(username=request.user)
        user.first_name = data["first_name"]
        user.last_name = data["last_name"]
        user.save()

        try:
            volunteer = get_volunteer_if_exists(user)
            volunteer_form = VolunteerForm(data, instance=volunteer)

            if volunteer_form.is_valid():
                volunteer = volunteer_form.save(commit=False)
                volunteer.user = user
                volunteer.save()
                return HTTPResponseHXRedirect("/volunteer/")
            else:
                context = {
                    "hx": check_if_hx(request),
                    "volunteer": get_volunteer_if_exists(request.user),
                    "errors": volunteer_form.errors,
                }
                return render(
                    request, "volunteer/partials/volunteer_form.html", context=context
                )
        except Exception as e:
            context = {
                    "hx": check_if_hx(request),
                    "volunteer": get_volunteer_if_exists(request.user),
                    "errors": e,
                }
            
            return render(
                request, "volunteer/partials/volunteer_form.html", context=context
            )

def emergency_contact_form(request, contact_id=None, delete=False):
    if request.method == "GET":
        if contact_id:
            try:
                emergency_contact = EmergencyContacts.objects.get(id=contact_id)
                if emergency_contact.volunteer.user == request.user:
                    if delete:
                        emergency_contact.delete()
                        return HTTPResponseHXRedirect("/volunteer/")
                    else:
                        context = {
                            "hx": check_if_hx(request),
                            "volunteer_id": get_volunteer_if_exists(request.user),
                            "contact": emergency_contact,
                            "edit": True,
                        }
                        return render(
                            request,
                            "volunteer/partials/emergency_contact_form.html",
                            context=context,
                        )
                else:
                    return HTTPResponseHXRedirect("/volunteer/")
            except ObjectDoesNotExist:
                return HTTPResponseHXRedirect("/volunteer/")

        else:
            context = {
                "hx": check_if_hx(request),
                "volunteer_id": get_volunteer_if_exists(request.user),
            }
            return render(
                request,
                "volunteer/partials/emergency_contact_form.html",
                context=context,
            )

    elif request.method == "POST":
        data = request.POST
        print(data)
        user = User.objects.get(username=request.user)
        volunteer = get_volunteer_if_exists(user)
        if contact_id:
            emergency_contact = EmergencyContacts.objects.get(id=contact_id)
            if emergency_contact.volunteer.user == request.user:
                emergency_contact_form = EmergencyContactsForm(
                    data, instance=emergency_contact
                )
            else:
                return HTTPResponseHXRedirect("/volunteer/")
        else:
            emergency_contact_form = EmergencyContactsForm(data)

        if emergency_contact_form.is_valid():
            emergency_contact = emergency_contact_form.save(commit=False)
            emergency_contact.volunteer = volunteer
            emergency_contact.save()
            return HTTPResponseHXRedirect("/volunteer/")
        else:
            context = {
                "hx": check_if_hx(request),
                "volunteer_id": get_volunteer_if_exists(request.user),
                "errors": emergency_contact_form.errors,
            }
            return render(
                request,
                "volunteer/partials/emergency_contact_form.html",
                context=context,
            )


def volunteer_address_form(request, address_id=None, delete=False):
    if request.method == "GET":
        if address_id:
            try:
                address = VolunteerAddress.objects.get(id=address_id)
                if address.volunteer.user == request.user:
                    if delete:
                        address.delete()
                        return HTTPResponseHXRedirect("/volunteer/")
                    else:
                        context = {
                            "hx": check_if_hx(request),
                            "volunteer_id": get_volunteer_if_exists(request.user),
                            "address": address,
                            "edit": True,
                        }
                        return render(
                            request,
                            "volunteer/partials/volunteer_address_form.html",
                            context=context,
                        )
                else:
                    return HTTPResponseHXRedirect("/volunteer/")
            except ObjectDoesNotExist:
                return HTTPResponseHXRedirect("/volunteer/")

        else:
            context = {
                "hx": check_if_hx(request),
                "volunteer_id": get_volunteer_if_exists(request.user),
            }
            return render(
                request,
                "volunteer/partials/volunteer_address_form.html",
                context=context,
            )

    elif request.method == "POST":
        data = request.POST
        print(data)
        user = User.objects.get(username=request.user)
        volunteer = get_volunteer_if_exists(user)
        if address_id:
            address = VolunteerAddress.objects.get(id=address_id)
            if address.volunteer.user == request.user:
                address_form = VolunteerAddressForm(data, instance=address)
            else:
                return HTTPResponseHXRedirect("/volunteer/")
        else:
            address_form = VolunteerAddressForm(data)

        if address_form.is_valid():
            address = address_form.save(commit=False)
            address.volunteer = volunteer
            address.save()
            return HTTPResponseHXRedirect("/volunteer/")
        else:
            context = {
                "hx": check_if_hx(request),
                "volunteer_id": get_volunteer_if_exists(request.user),
                "errors": address_form.errors,
            }
            return render(
                request,
                "volunteer/partials/volunteer_address_form.html",
                context=context,
            )


def volunteer_conditions_form(request, condition_id=None, delete=False):
    if request.method == "GET":
        if condition_id:
            try:
                condition = VolunteerConditions.objects.get(id=condition_id)
                if condition.volunteer.user == request.user:
                    if delete:
                        condition.delete()
                        return HTTPResponseHXRedirect("/volunteer/")
                    else:
                        context = {
                            "hx": check_if_hx(request),
                            "volunteer_id": get_volunteer_if_exists(request.user),
                            "condition": condition,
                            "edit": True,
                        }
                        return render(
                            request,
                            "volunteer/partials/volunteer_conditions_form.html",
                            context=context,
                        )
                else:
                    return HTTPResponseHXRedirect("/volunteer/")
            except ObjectDoesNotExist:
                return HTTPResponseHXRedirect("/volunteer/")

        else:
            context = {
                "hx": check_if_hx(request),
                "volunteer_id": get_volunteer_if_exists(request.user),
            }
            return render(
                request,
                "volunteer/partials/volunteer_conditions_form.html",
                context=context,
            )

    elif request.method == "POST":
        data = request.POST
        print(data)
        user = User.objects.get(username=request.user)
        volunteer = get_volunteer_if_exists(user)
        if condition_id:
            condition = VolunteerConditions.objects.get(id=condition_id)
            if condition.volunteer.user == request.user:
                condition_form = VolunteerConditionsForm(data, instance=condition)
            else:
                return HTTPResponseHXRedirect("/volunteer/")
        else:
            condition_form = VolunteerConditionsForm(data)

        if condition_form.is_valid():
            condition = condition_form.save(commit=False)
            condition.volunteer = volunteer
            condition.save()
            return HTTPResponseHXRedirect("/volunteer/")
        else:
            context = {
                "hx": check_if_hx(request),
                "volunteer_id": get_volunteer_if_exists(request.user),
                "errors": condition_form.errors,
            }
            return render(
                request,
                "volunteer/partials/volunteer_conditions_form.html",
                context=context,
            )


def sign_up(request):
    if request.method == "GET":
        return render(request, "volunteer/sign_up.html", {"hx": check_if_hx(request)})
    elif request.method == "POST":
        data = request.POST
        print(data)
        # create django user
        user = User.objects.create_user(data["email"], data["email"], data["password"])
        user.save()
        # create volunteer -> redirect to onboarding
        return HTTPResponseHXRedirect("/volunteer")


def user_logout(request):
    logout(request)
    return HttpResponseRedirect("/volunteer")
