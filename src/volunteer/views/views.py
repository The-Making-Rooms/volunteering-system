from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from volunteer.models import (
    Volunteer,
    VolunteerAddress,
    EmergencyContacts,
    VolunteerConditions,
    VolunteerSupplementaryInfo

)
from opportunities.models import Registration, VolunteerRegistrationStatus, RegistrationAbsence, RegistrationStatus
from django.core.exceptions import ObjectDoesNotExist
import random
from django.contrib.auth.decorators import login_required
from commonui.views import check_if_hx, HTTPResponseHXRedirect, redirect_admins
from datetime import datetime, date
from django.contrib.auth.models import User
from django.contrib.auth import logout
from ..forms import (
    VolunteerForm,
    VolunteerAddressForm,
    EmergencyContactsForm,
    VolunteerConditionsForm,
)

from organisations.models import OrganisationInterest, Organisation
import random

from django.core.mail import send_mail

from volunteer.models import MentorNotes, MentorRecord, MentorSession

from forms.models import FormResponseRequirement, Form as FormModel, Question, Answer, Response

from organisations.models import OrganisationAdmin
import re

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
        if request.user.is_superuser:
            print("user is superuser")
            return HttpResponseRedirect("/org_admin")
        elif OrganisationAdmin.objects.filter(user=request.user).exists():
            return HttpResponseRedirect("/org_admin")
    
    if request.user.is_authenticated:
        current_user = request.user
        try:
            volunteer_profile = Volunteer.objects.get(user=current_user)
            print(volunteer_profile)
            
            #check for incomplete forms that with required_on_signup = True
            req_forms = FormModel.objects.filter(required_on_signup=True)
            for form in req_forms:
                if FormResponseRequirement.objects.filter(user=current_user, form=form).exists() == False:
                    #Create a form Response Requirement, which lets the system know that the user has to fill out this form
                    form_req = FormResponseRequirement(user=current_user, form=form)
                    form_req.save()
                    return HTTPResponseHXRedirect("/forms/" + str(form.id))
                else:
                    #check if the form has been completed
                    form_req = FormResponseRequirement.objects.get(user=current_user, form=form)
                    if form_req.completed == False:
                        #redirect to form
                        return HttpResponseRedirect("/forms/" + str(form.id))
                    else:
                        continue
            
            
            incomplete_forms = FormResponseRequirement.objects.filter(user=current_user, completed=False)
            print(incomplete_forms)
            
            supp_info = VolunteerSupplementaryInfo.objects.filter(volunteer=volunteer_profile)
            
            organisaton_interests = OrganisationInterest.objects.filter(volunteer=volunteer_profile)

            mentor_profile = MentorRecord.objects.filter(volunteer=volunteer_profile)
            
            print(mentor_profile)
            if mentor_profile.exists():
                mentor_profile = mentor_profile.first()
                mentor_notes = MentorNotes.objects.filter(MentorRecord=mentor_profile)
                mentor_sessions = MentorSession.objects.filter(mentor_record=mentor_profile)
            else:
                mentor_profile = None
                mentor_notes = None
                mentor_sessions = None

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
                "forms": incomplete_forms,
                "link_active": "volunteer",
                "supp_info": supp_info,
                
                "mentor_profile": mentor_profile,
                "mentor_notes": mentor_notes,
                "mentor_sessions": mentor_sessions,
                "organisation_interests": organisaton_interests, 
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
            
            #Send confirmation email
            send_m = send_mail(
                'Chip in - Volunteer Event Confirmation',
                'You have stopped volunteering for the event: ' + registration.opportunity.name,
                None,
                [current_user.email],
                fail_silently=True,
            )
            
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
            "organisations": Organisation.objects.all(),
            "initial_onboarding": True,
        }
        return render(
            request, "volunteer/partials/volunteer_form.html", context=context
        )

    elif request.method == "POST":
        data = request.POST
        user = User.objects.get(username=request.user)
        user.first_name = data["first_name"]
        user.last_name = data["last_name"]
        
        temp_username = data["first_name"] + data["last_name"] + "".join(random.choices("0123456789", k=5))
        
        while User.objects.filter(username=temp_username).exists():
           temp_username = data["first_name"] + data["last_name"] + "".join(random.choices("0123456789", k=5))
        user.username = temp_username
        user.save()
        
        followed_organisations = data.getlist("followed_organisations")
        

        try:
            volunteer = get_volunteer_if_exists(user)
            volunteer_form = VolunteerForm(data, instance=volunteer)

            if volunteer_form.is_valid():
                
                volunteer = volunteer_form.save(commit=False)
                min_age = 16
                
                if volunteer.date_of_birth:
                    age = datetime.now().year - volunteer.date_of_birth.year
                    if age < min_age:
                        return render(request, "volunteer/partials/error.html", context={"hx": check_if_hx(request), "volunteer": get_volunteer_if_exists(request.user), "errors": ["You must be between 16 and 30 years old to volunteer."]})
                
                if user.first_name == "" or user.last_name == "":
                    return render(request, "volunteer/partials/error.html", context={"hx": check_if_hx(request), "volunteer": get_volunteer_if_exists(request.user), "errors": ["First and last name are required"]})
    
                volunteer.user = user
                volunteer.save()
                
                #emergency contacts
                
                contact_first_name = data["emergency_contact_name"]
                contact_last_relation = data["emergency_contact_relation"]
                contact_phone = data["emergency_contact_phone_number"]
                contact_email = data["emergency_contact_email"]
                
                #Check if either name, relation is empty
                if contact_first_name == "" or contact_last_relation == "":
                    return render(request, "volunteer/partials/error.html", context={"hx": check_if_hx(request), "volunteer": get_volunteer_if_exists(request.user), "errors": ["Emergency contact name and relation are required"]})
                
                if contact_phone == "" and contact_email == "":
                    return render(request, "volunteer/partials/error.html", context={"hx": check_if_hx(request), "volunteer": get_volunteer_if_exists(request.user), "errors": ["Emergency contact phone number or email is required"]})
                
                conatact = EmergencyContacts(
                    volunteer=volunteer,
                    name=contact_first_name,
                    relation=contact_last_relation,
                    phone_number=contact_phone,
                    email=contact_email,
                )
                
                conatact.save()
                
                #Post code
                postcode = data["post_code"]
                regex = "([Gg][Ii][Rr] 0[Aa]{2})|((([A-Za-z][0-9]{1,2})|(([A-Za-z][A-Ha-hJ-Yj-y][0-9]{1,2})|(([A-Za-z][0-9][A-Za-z])|([A-Za-z][A-Ha-hJ-Yj-y][0-9][A-Za-z]?))))\s?[0-9][A-Za-z]{2})"
                
                if postcode == "":
                    return render(request, "volunteer/partials/error.html", context={"hx": check_if_hx(request), "volunteer": get_volunteer_if_exists(request.user), "errors": ["Postcode is required"]})
                
                if not re.match(regex, postcode):
                    return render(request, "volunteer/partials/error.html", context={"hx": check_if_hx(request), "volunteer": get_volunteer_if_exists(request.user), "errors": ["Invalid postcode"]})
                
                address = VolunteerAddress.objects.filter(volunteer=volunteer, postcode=postcode)
                if not address.exists():
                    address = VolunteerAddress(volunteer=volunteer, postcode=postcode)
                    address.save()
                
                
                
                for organisation in followed_organisations:
                    org = OrganisationInterest(volunteer=volunteer, organisation_id=organisation)
                    org.save()
                
                return render(request, "volunteer/partials/redirect.html")
            else:
                context = {
                    "hx": check_if_hx(request),
                    "volunteer": get_volunteer_if_exists(request.user),
                    "errors": volunteer_form.errors,
                }
                return render(
                    request, "volunteer/partials/error.html", context=context
                )
        except Exception as e:
            context = {
                    "hx": check_if_hx(request),
                    "volunteer": get_volunteer_if_exists(request.user),
                    "errors": e,
                }
            
            return render(
                request, "volunteer/partials/error.html", context=context
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

def volunteer_supp_info_form(request, supp_info_id):
    info = VolunteerSupplementaryInfo.objects.get(id=supp_info_id)
    if info.volunteer == Volunteer.objects.get(user=request.user):
        if request.method == "GET":
            context = {
                "hx": check_if_hx(request),
                "volunteer": get_volunteer_if_exists(request.user),
                "supp_info": info,
            }
            return render(
                request, "volunteer/partials/volunteer_supp_info_form.html", context=context
            )
        elif request.method == "POST":
            data = request.POST
            if len(data["supp_info"]) > 0:
                info.data = data["supp_info"]
                info.save()
            return HTTPResponseHXRedirect("/volunteer/")

def sign_up(request):
    if request.method == "GET":
        return render(request, "volunteer/sign_up.html", {"hx": check_if_hx(request)})
    elif request.method == "POST":
        data = request.POST
        
        if User.objects.filter(email=data["email"]).exists():
            return render(request, "commonui/error.html", {"hx": check_if_hx(request), "error": "Email already in use"})
        
        if data["password"] != data["password_confirm"]:
            return render(request, "commonui/error.html", {"hx": check_if_hx(request), "error": "Passwords do not match"})
        #print(data)
        username = "".join(random.choices("abcdefghijklmnopqrstuvwxyz", k=10))
        #ensure a user with that username does not exist
        while User.objects.filter(username=username).exists():
            username = "".join(random.choices("abcdefghijklmnopqrstuvwxyz", k=10))
        # create django user
        user = User.objects.create_user(username, data["email"], data["password"])
        user.save()
        # create volunteer -> redirect to onboarding
        return HTTPResponseHXRedirect("/volunteer")

def volunteer_absence(request, registration_id):
    if request.method == "POST":
        data = request.POST
        print("POST")
        print(data)
        registration = Registration.objects.get(id=registration_id)
        #checkboxes benin with event_<01/05/24>
        print(data)
        #delete all absences
        RegistrationAbsence.objects.filter(registration=registration).delete()
        dates = request.POST.getlist("event")
        print(dates)
        for date in dates:
            #each date is in the format event_<01/05/24>
            print(date)
            date = date.split("_")[1]
            
            date = datetime.strptime(date, "%d/%m/%y")
            absence = RegistrationAbsence(registration=registration, date=date)
            absence.save()
            
        return HTTPResponseHXRedirect("/volunteer/your-opportunities")
    volunteer = Volunteer.objects.get(user=request.user)
    opportunity = Registration.objects.get(id=registration_id).opportunity
    
    #get all recurrences between now and end of month
    occourances = opportunity.recurrences.between(
        datetime.now(),
        datetime(datetime.now().year, datetime.now().month, 1).replace(day=1, month=datetime.now().month+1),
        inc=True
    )
    
    template_occourances = []
    dates = [absence.date for absence in RegistrationAbsence.objects.filter(registration=registration_id)]
    print(dates)
    print(dates)
    for occourance in occourances:
        print(type(occourance.date()))
        
        occour = {
            "start_time": opportunity.start_time,
            "end_time": opportunity.end_time,
            "disabled": True if occourance < datetime.now() else False,
            "date": occourance.date(),
            "absent_exists": True if occourance.date() in dates else False,
        }
        
        template_occourances.append(occour)
        
    return render(request, "volunteer/partials/volunteer_absence.html", {"hx": check_if_hx(request), "volunteer": volunteer, "occourances": template_occourances, "registration_id": registration_id})

def user_logout(request):
    logout(request)
    return HttpResponseRedirect("/volunteer")

