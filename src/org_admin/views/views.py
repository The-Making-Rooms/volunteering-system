from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse_lazy
from ..models import OrganisationAdmin
from commonui.views import check_if_hx, HTTPResponseHXRedirect
from webpush import  send_user_notification
from organisations.models import Location, Video as OrgVideo, Image as OrgImage, Link, LinkType, Organisation, Badge, VolunteerBadge, BadgeOpporunity, OrganisationInterest, OrganisationSection
from opportunities.models import Opportunity, Image as OppImage, Video as OppVideo, Registration, OpportunityView, Location as OppLocation, Tag, LinkedTags, Benefit, OpportunityBenefit
from communications.models import Message, Chat, AutomatedMessage
from opportunities.models import Opportunity, Image as OppImage, Video as OppVideo, Registration, OpportunityView, SupplimentaryInfoRequirement, VolunteerRegistrationStatus, RegistrationAbsence, RegistrationStatus, Icon, Benefit, Tag, LinkedTags
from volunteer.models import Volunteer, VolunteerConditions, VolunteerSupplementaryInfo, SupplementaryInfo, VolunteerAddress, EmergencyContacts
from .common import check_ownership
from datetime import datetime, timedelta, date
import requests
from requests_oauthlib import OAuth1
from django.conf import settings
import json
import os
import csv
from django.core.files import File
from io import BytesIO
from django.core.files.base import ContentFile
from django.contrib.auth.views import PasswordResetView
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.password_validation import validate_password
from .auth import sign_in
from django.contrib.auth.models import User
import random
from forms.models import Form, Response, Question


class ResetPasswordView(SuccessMessageMixin, PasswordResetView):
    template_name = "org_admin/password_reset.html"
    email_template_name = "org_admin/password_reset_email.html"
    subject_template_name = "org_admin/password_reset_subject.txt"
    success_message = (
        "We've emailed you instructions for setting your password, "
        "if an account exists with the email you entered. You should receive them shortly."
        " If you don't receive an email, "
        "please make sure you've entered the address you registered with, and check your spam folder."
    )
    success_url = reverse_lazy("password_reset_sent")
    

    # add hx context to the view
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["hx"] = check_if_hx(self.request)
        return context


def password_reset_sent(request):
    return render(
        request, "org_admin/password_reset_sent.html", {"hx": check_if_hx(request)}
    )
    
def utils_set_benefit_org(request):
    if not request.user.is_superuser:
        return HttpResponse("You do not have permission to run this script")
    
    opp_benefits = OpportunityBenefit.objects.all()
    for opp_benefit in opp_benefits:
        benefit = opp_benefit.benefit #
        org = opp_benefit.opportunity.organisation
        
        if benefit.organisation != org:
            benefit.organisation = org
            benefit.save()
            
    return HttpResponse("Done")
        
    
def utils_set_random_password(request):
    if not request.user.is_superuser:
        return HttpResponse("You do not have permission to run this script")
    
    users = User.objects.filter()
    for user in users:
        if user.has_usable_password():
            continue
        else:
            user.set_password("".join(random.choices("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890", k=24)))
            user.save()
        
    return HttpResponse("Done")
            
    
def utils_set_emails_lower(request):
    if not request.user.is_superuser:
        return HttpResponse("You do not have permission to run this script")
    
    users = User.objects.all()
    for user in users:
        user.email = user.email.lower()
        user.username = user.email
        user.save()
    return HttpResponse("Done")


def utils_fix_festival_followers(request):
    if not request.user.is_superuser:
        return HttpResponse("You do not have permission to run this script")
    
    org = Organisation.objects.get(name="British Textile Biennial")
    
    festival_fom = Organisation.objects.get(name="National Festival of Making")
    festival_light = Organisation.objects.get(name="Blackburn Festival of Light")
    
    followers = OrganisationInterest.objects.filter(organisation=org)
    
    for follower in followers:
        #add followers if they dont exist
        if not OrganisationInterest.objects.filter(organisation=festival_fom, volunteer=follower.volunteer).exists():
            OrganisationInterest.objects.create(organisation=festival_fom, volunteer=follower.volunteer)
            
        if not OrganisationInterest.objects.filter(organisation=festival_light, volunteer=follower.volunteer).exists():
            OrganisationInterest.objects.create(organisation=festival_light, volunteer=follower.volunteer)
            
    
    return HttpResponse("Done")
    
# Create your views here.
def volunteer_admin(request):
    #List of volunteers without repeating
    if request.user.is_superuser:
        volunteers = Volunteer.objects.all()
        
        organisation_admins = OrganisationAdmin.objects.all()
        
        #remove organisation admins from the list
        for org_admin in organisation_admins:
            volunteers = volunteers.exclude(user__id=org_admin.user.id)
            
        #remove superusers from the list
        volunteers = volunteers.exclude(user__is_superuser=True)
        
        context = {
            "hx": check_if_hx(request),
            "unique_volunteers": volunteers,
        }
        
    else:
        registrations = Registration.objects.filter(opportunity__organisation=OrganisationAdmin.objects.get(user=request.user).organisation)
        unique_volunteers = Volunteer.objects.filter(id__in=registrations.values_list('volunteer', flat=True)).distinct()
        
        organisation_admins = OrganisationAdmin.objects.all()
        
        #remove organisation admins from the list
        for org_admin in organisation_admins:
            unique_volunteers = unique_volunteers.exclude(user__id=org_admin.user.id)
        
        #remove superusers from the list
        unique_volunteers = unique_volunteers.exclude(user__is_superuser=True)
        
        print(unique_volunteers)
        context = {
            "hx": check_if_hx(request),
            "unique_volunteers": unique_volunteers,
        }
        
    return render(request, "org_admin/volunteer_admin.html", context)



def opportunity_admin(request, error=None, success=None):
    
    if request.user.is_superuser:
        opportunities = Opportunity.objects.all()

    else:
        opportunities = Opportunity.objects.filter(
            organisation=OrganisationAdmin.objects.get(user=request.user).organisation
        )

    []

    for opportunity in opportunities:
        opportunity.registrations = Registration.objects.filter(opportunity=opportunity).count()
        opportunity.views = OpportunityView.objects.filter(opportunity=opportunity).count()
        

    return render(
        request,
        "org_admin/opportunity_admin.html",
        {"hx": check_if_hx(request),
         "opportunities": opportunities,
         "superuser": request.user.is_superuser,
         "error": error,
        "success": success,
         },
    )
    
def get_filtered_opportunities(request):
    if request.method == "POST":
        data = request.POST
        search_term = data["search"]
        
        opportunities = None
        
        if request.user.is_superuser:
            opportunities = Opportunity.objects.filter(name__icontains=search_term) | Opportunity.objects.filter(description__icontains=search_term) | Opportunity.objects.filter(organisation__name__icontains=search_term) | Opportunity.objects.filter(id__in=LinkedTags.objects.filter(tag__tag__icontains=search_term).values_list('opportunity', flat=True))
        else:
            admin_org = OrganisationAdmin.objects.get(user=request.user).organisation
            Opportunity.objects.filter(organisation=admin_org).filter(name__icontains=search_term) | Opportunity.objects.filter(organisation=admin_org).filter(description__icontains=search_term) | Opportunity.objects.filter(organisation=admin_org).filter(organisation__name__icontains=search_term) | Opportunity.objects.filter(organisation=admin_org).filter(id__in=LinkedTags.objects.filter(tag__tag__icontains=search_term).values_list('opportunity', flat=True))

        for opportunity in opportunities:
            opportunity.registrations = Registration.objects.filter(opportunity=opportunity).count()
            opportunity.views = OpportunityView.objects.filter(opportunity=opportunity).count()
            
        context = {
            "hx": check_if_hx(request),
            "opportunities": opportunities,
            "superuser": request.user.is_superuser,
        }
        
        return render(request, "org_admin/opportunity_admin_table.html", context=context)
    else:
        if request.user.is_superuser:
            opportunities = Opportunity.objects.all()
        else:
            opportunities = Opportunity.objects.filter(
                organisation=OrganisationAdmin.objects.get(user=request.user).organisation
            )
        
        for opportunity in opportunities:
            opportunity.registrations = Registration.objects.filter(opportunity=opportunity).count()
            opportunity.views = OpportunityView.objects.filter(opportunity=opportunity).count()
            
        context = {
            "hx": check_if_hx(request),
            "opportunities": opportunities,
            "superuser": request.user.is_superuser,
        }
        
        return render(request, "org_admin/opportunity_admin_table.html", context=context)

            

def upload_organisation_logo(request, organisation_id=None):
    if request.method == "GET":
        if request.user.is_superuser:
            return render(request, "org_admin/partials/file_upload.html", {"hx": check_if_hx(request), "upload_url": "/org_admin/upload_organisation_logo/{}/".format(organisation_id)})
        return render(request, "org_admin/partials/file_upload.html", {"hx": check_if_hx(request), "upload_url": "/org_admin/upload_organisation_logo/"})
    elif request.method == "POST":
        
        if organisation_id and request.user.is_superuser:
            org = Organisation.objects.get(id=organisation_id)
        else:
            org = OrganisationAdmin.objects.get(user=request.user).organisation

        file = request.FILES["file"]
        file_type = file.content_type.split("/")[1]
        if file_type in ["png", "jpg", "jpeg"]:
            org.logo = file
            org.save()
            if organisation_id and request.user.is_superuser:
                return HTTPResponseHXRedirect("/org_admin/organisations/{}/".format(organisation_id))
            return HTTPResponseHXRedirect("/org_admin/details/")

def delete_opportunity(request, id):
    opportunity = Opportunity.objects.get(id=id)
    if check_ownership(request, opportunity):
        opportunity.delete()
    else:
        return opportunity_admin(request, error="You do not have permission to delete this opportunity")
    return opportunity_admin(request)


def create_new_organisation(request):
    if request.user.is_superuser:
        if request.method == "POST":
            print(request.FILES, request.POST)
            data = request.POST
            logo = request.FILES["logo"]
            
            
            
            org = Organisation.objects.create(
                name=data["name"],
                description=data["description"],
                logo = logo,
            )
            return HTTPResponseHXRedirect("/org_admin/organisations/{}/".format(org.id))
        return render(request, "org_admin/create_new_organisation.html", {"hx": check_if_hx(request)})
    else:
        return opportunity_admin(request, error="You do not have permission to create an organisation")

def details(request, error=None, success=None, organisation_id=None):
    if not request.user.is_authenticated:
        return sign_in(request)
    print(request.user.is_superuser)
    if request.method == "POST":
        if organisation_id and request.user.is_superuser:
            org = Organisation.objects.get(id=organisation_id)
        elif request.user.is_superuser:
            request.method = "GET"
            return render(request, "org_admin/superuser_organisation_admin.html", {"hx": check_if_hx(request), "organisations": Organisation.objects.all()})
        else:
            org = OrganisationAdmin.objects.get(user=request.user).organisation
        
        data = request.POST
        org.name = data["name"]
        org.description = data["description"]
        org.save()
        request.method = "GET"
        return details(request, organisation_id=organisation_id, success="Organisation details updated")
    else:
        try:
            if organisation_id and request.user.is_superuser:
                organisation = Organisation.objects.get(id=organisation_id)
            elif request.user.is_superuser:
                return render(request, "org_admin/superuser_organisation_admin.html", {"hx": check_if_hx(request), "organisations": Organisation.objects.all()})
            else:
                organisation = OrganisationAdmin.objects.get(user=request.user).organisation
        except OrganisationAdmin.DoesNotExist:
            return HttpResponseRedirect("/volunteer/")


        org_videos = OrgVideo.objects.filter(organisation=organisation)
        org_images = OrgImage.objects.filter(organisation=organisation)
        badges = Badge.objects.filter(organisation=organisation)
        link_types = LinkType.objects.all()
        automated_message = AutomatedMessage.objects.get(organisation=organisation) if AutomatedMessage.objects.filter(organisation=organisation).exists() else None
        supp_info = SupplementaryInfo.objects.filter(organisation=organisation)
        interested_vols = OrganisationInterest.objects.filter(organisation=organisation)
        sections = OrganisationSection.objects.filter(organisation=organisation)
        
        link_obj = []
        
        for link in link_types:
            link_obj.append({
                "link": Link.objects.get(organisation=organisation, link_type=link).url if Link.objects.filter(organisation=organisation, link_type=link).exists() else None,
                "type": link,
            })
        context = {
            "hx": check_if_hx(request),
            "locations": Location.objects.filter(organisation=organisation),
            "organisation": organisation,
            "org_videos": org_videos,
            "org_images": org_images,
            "badges": badges,
            "link_types": link_obj,
            "supp_info": supp_info,
            "automated_message": automated_message,
            "locations": Location.objects.filter(organisation=organisation),
            "error": error,
            "success": success,
            "interested_vols": interested_vols,
            "superuser": request.user.is_superuser,
            "sections": sections,
        }

        return render(request, "org_admin/organisation_details_admin.html", context)

def supplementary_info(request, org_id=None):        
    if request.method == "POST":
        data = request.POST
        if org_id and request.user.is_superuser:
            org = Organisation.objects.get(id=org_id)
        else:
            org = OrganisationAdmin.objects.get(user=request.user).organisation
        supp_info = SupplementaryInfo.objects.create(
            organisation=org,
            title=data["name"],
            description=data["description"],
        )
        request.method="GET"
        return details(request, organisation_id=org_id, success="Supplementary info added")

def delete_supplementary_info(request, id):
    supp_info = SupplementaryInfo.objects.get(id=id)
    if check_ownership(request, supp_info):
        supp_info.delete()
    else:
        return details(request, error="You do not have permission to delete this supplementary info")
    return details(request, organisation_id=supp_info.organisation.id, success="Supplementary info deleted")



def volunteer_details_admin(request, id):
    volunteer = Volunteer.objects.get(id=id)

    if not request.user.is_superuser:
        volunteer_part_of_org = Registration.objects.filter(volunteer=volunteer, opportunity__organisation=OrganisationAdmin.objects.get(user=request.user).organisation).exists()
        if not volunteer_part_of_org:
            return volunteer_admin(request, error="You do not have permission to view this volunteer")
    
    
    
    
    if request.user.is_superuser:
        print("superuser")
        registrations = Registration.objects.filter(volunteer=volunteer)
        vol_supp_info = VolunteerSupplementaryInfo.objects.filter(volunteer=volunteer)
    else:
        registrations = Registration.objects.filter(volunteer=volunteer, opportunity__organisation=OrganisationAdmin.objects.get(user=request.user).organisation)
        org_supp_info = SupplimentaryInfoRequirement.objects.filter(opportunity__in=registrations.values_list('opportunity', flat=True))
        vol_supp_info = VolunteerSupplementaryInfo.objects.filter(volunteer=volunteer, info__id__in=org_supp_info.values_list('info', flat=True))
    
    for registration in registrations:
        opportunity = registration.opportunity
        stopped_status = RegistrationStatus.objects.get(status="stopped")
        started_status = RegistrationStatus.objects.get(status="active")
        
        if VolunteerRegistrationStatus.objects.filter(registration=registration, registration_status=started_status).exists():
        
            volunteer_start = VolunteerRegistrationStatus.objects.get(registration=registration, registration_status=started_status).date
            
            
            dateTimeA = datetime.combine(date.today(), opportunity.start_time)
            dateTimeB = datetime.combine(date.today(), opportunity.end_time)
            # Get the difference between datetimes (as timedelta)
            dateTimeDifference = dateTimeB - dateTimeA
            print(dateTimeDifference)
            
            
            start_date_0_0 = datetime(volunteer_start.date().year, volunteer_start.date().month, volunteer_start.date().day, 0, 0)
            
            if VolunteerRegistrationStatus.objects.filter(registration=registration, registration_status=stopped_status).exists():
                print("stopped as of: ", VolunteerRegistrationStatus.objects.get(registration=registration, registration_status=stopped_status).date.date())
                is_stopped = VolunteerRegistrationStatus.objects.get(registration=registration, registration_status=stopped_status)
                is_stopped_23_59 = datetime(is_stopped.date.date().year, is_stopped.date.date().month, is_stopped.date.date().day, 23, 59)
            else:
                now= datetime.now()
                is_stopped_23_59 = datetime(now.year, now.month, now.day, 23, 59)
            
            recurrences = len(opportunity.recurrences.between(
                start_date_0_0,
                is_stopped_23_59,
                inc=True
            ))
            
            absences = RegistrationAbsence.objects.filter(registration=registration).count()
            hours = dateTimeDifference.total_seconds() / 3600 * recurrences - absences
        else:
            print("not been approved")
            hours = 0
            
            
        latest_status = VolunteerRegistrationStatus.objects.filter(registration=registration).last()
        
        
    
    conditions = VolunteerConditions.objects.filter(volunteer=volunteer)
    addresses = VolunteerAddress.objects.filter(volunteer=volunteer)
    emergency_contacts = EmergencyContacts.objects.filter(volunteer=volunteer)
    interests = OrganisationInterest.objects.filter(volunteer=volunteer)
    
    context = {
        "hx": check_if_hx(request),
        "volunteer": volunteer,
        "registrations": registrations,
        "conditions": conditions,
        "vol_supp_info": vol_supp_info,
        "addresses": addresses,
        "contacts": emergency_contacts,
        "interests": interests,
        "superuser": request.user.is_superuser,
    }
    
    return render(request, "org_admin/volunteer_details_admin.html", context=context)
    
def chats(request):
    organisation = OrganisationAdmin.objects.get(user=request.user).organisation
    chats = Chat.objects.filter(organisation=organisation)
    context = {
        "hx": check_if_hx(request),
        "chats": chats,
    }
    return render(request, "org_admin/chats.html", context=context)
    
def chat(request, id):
    chat = Chat.objects.get(id=id)
    messages = Message.objects.filter(chat=chat)
    if request.method == "POST":
        data = request.POST
        message = Message.objects.create(
            chat=chat,
            sender=request.user,
            content=data["content"],
        )
        
        for user in chat.users:
            send_user_notification(user, {"message": message.content}) if user != request.user else None
        
        return chat(request, id)
    else:
        if chat.organisation != OrganisationAdmin.objects.get(user=request.user).organisation:
            return chats(request, error="You do not have permission to view this chat")
        
        context = {
            "hx": check_if_hx(request),
            "chat": chat,
            "messages": messages,
        }
        return render(request, "org_admin/chat.html", context=context)
    
    
def manage_link(request, link_id=None, delete=False):
    if request.method == "GET":
        if link_id:
            if delete:
                link = Link.objects.get(id=link_id)
                link.delete()
                return details(request)
            link = Link.objects.get(id=link_id)
            link_types = LinkType.objects.all()
            return render(request, "org_admin/partials/edit_link.html", context={"hx": check_if_hx(request), "link": link, "link_types": link_types})
        return render(request, "org_admin/partials/edit_link.html", context={"hx": check_if_hx(request), "link": None, "link_types": LinkType.objects.all()})
    
    if request.method == "POST":
        org = OrganisationAdmin.objects.get(user=request.user).organisation
        data = request.POST
        print(data)
        if data["link_id"]:
            link = Link.objects.get(id=data["link_id"])
            link.link_type = LinkType.objects.get(id=data["type"])
            link.url = data["url"]
            link.name = data["name"]
            link.save()
            request.method = "GET"
            return details(request)
        link = Link.objects.create(
            organisation=org,
            url=data["url"],
            name=data["name"],
            link_type=LinkType.objects.get(id=data["type"]),
        )
        request.method = "GET"
        return details(request)

def upload_icons(request):
    if request.method == "POST":
        files = request.FILES.getlist('file')
        
        for file in files:
            print(file)
            icons = Icon.objects.filter(name=file.name).exists()
            if not icons:
                icon = Icon(
                    icon = file,
                    name = file.name.split('.')[0]
                )
            icon.save()
            print("Icon Name: {} File: {}".format(file.name.split('.')[0], file))
        return HttpResponse('Icons Uploaded')

    else:
        return render(request, 'org_admin/partials/file_upload.html', context={
            "hx": check_if_hx(request),
            "upload_url": "/org_admin/upload_icons/"
        })
        
def icons(request):
        auth = OAuth1(settings.NOUN_PROJECT_API_KEY, settings.NOUN_PROJECT_SECRET_KEY)
        endpoint = "https://api.thenounproject.com/v2/icon/"
        params = {
            "limit": 10,
            "query": request.POST["search"]
        }
        
        response = requests.get(endpoint, auth=auth, params=params)
        resp = json.loads(response.text)

        if len(json.loads(response.text)["icons"]) == 0:
            return HttpResponse("No icons found")
        
        icons = [json.loads(response.text)["icons"][i] for i in range(10)]

        context = {
            "results" : icons,
        }
        return render(request, "org_admin/partials/icon_results.html", context=context)
        
        
def automated_messages(request, id=None):
    if request.method == "POST":
        data = request.POST
        if request.user.is_superuser:
            org = Organisation.objects.get(id=id)
        else:
            org = OrganisationAdmin.objects.get(user=request.user).organisation
            
        if AutomatedMessage.objects.filter(organisation=org).exists():
            message = AutomatedMessage.objects.get(organisation=org)
            message.content = data["message"]
            message.save()
            
        else:
            message = AutomatedMessage.objects.create(
                organisation=org,
                content=data["message"]
            )
        
        request.method = "GET"
        return details(request, organisation_id=id, success="Automated message updated")
    
        
def manage_badge(request, badge_id=None, organisation_id=None, delete=False):
    if request.method == "POST":
        try:
            data = request.POST
            if badge_id:
                badge = Badge.objects.get(id=badge_id)
                if not check_ownership(request, badge):
                    return details(request, error="You do not have permission to edit this badge")
                badge.name = data["name"]
                badge.description = data["description"]
                badge.save()
                add_icon(badge, data["icon"])
                request.method = "GET"
                return details(request, organisation_id=badge.organisation.id, success="Badge updated")
            else:
                if request.user.is_superuser:
                    org = Organisation.objects.get(id=organisation_id)
                else:
                    org = OrganisationAdmin.objects.get(user=request.user).organisation
                    
                if data["name"] == "" or data["description"] == "":
                    request.method = "GET"
                    return details(request, organisation_id=org.id, error="Please ensure all fields are filled")    
                badge = Badge(
                    name=data["name"],
                    description=data["description"],
                    organisation=org,
                )
                badge.save()
                add_icon(badge, data["icon"])
                
                request.method = "GET"
                return details(request, organisation_id=org.id, success="Badge created")
        except Exception as e:
            print(e)
            request.method = "GET"
            return details(request, error="An error occoured. Please ensure all fields are filled.")
    if request.method == "GET":
        if badge_id:
            if delete:
                badge = Badge.objects.get(id=badge_id)
                if not check_ownership(request, badge):
                    return details(request, error="You do not have permission to delete this badge")
                badge.delete()
                return details(request, organisation_id=badge.organisation.id, success="Badge deleted") 
            
            badge = Badge.objects.get(id=badge_id)
            if check_ownership(request, badge):
                return render(request, "org_admin/partials/add_badge.html", context={"hx": check_if_hx(request), "badge": badge, "superuser": request.user.is_superuser})
            else:
                return details(request, error="You do not have permission to edit this badge")
        else:   
            if request.user.is_superuser:
                org = Organisation.objects.get(id=organisation_id) 
                return render(request, "org_admin/partials/add_badge.html", context={"hx": check_if_hx(request), "badge": None, "organisation": org, "superuser": request.user.is_superuser})
            else:    
                return render(request, "org_admin/partials/add_badge.html", context={"hx": check_if_hx(request), "badge": None, "superuser": request.user.is_superuser})
        
        
def add_icon(badge, icon_id):

    auth = OAuth1(settings.NOUN_PROJECT_API_KEY, settings.NOUN_PROJECT_SECRET_KEY)
    endpoint = "https://static.thenounproject.com/png/{}-200.png"
    #download file into bytesIO
    img_bytes = requests.get(endpoint.format(icon_id), auth=auth).content
    bytes_io = BytesIO(img_bytes)
    badge.image.save("{}.png".format(icon_id), ContentFile(bytes_io.getvalue()))
    badge.save()


def assign_badge_to_volunteer(request, volunteer_id, badge_id):
    badge = Badge.objects.get(id=badge_id)
    if not check_ownership(request, badge):
        return volunteer_admin(request, error="You do not have permission to assign this badge")
    volunteer = Volunteer.objects.get(id=volunteer_id)
    #remove status where = stopped
    
    if not request.user.is_superuser:
        non_acceptable_status = RegistrationStatus.objects.filter().exclude(status="active")
        registrations = Registration.objects.filter(volunteer=volunteer)
        volunteer_is_active = VolunteerRegistrationStatus.objects.filter(registration__in=registrations).exclude(registration_status__in=non_acceptable_status).exists()
        if not volunteer_is_active:
            return volunteer_admin(request, error="Volunteer is not active")
    
    else:
        VolunteerBadge.objects.create(
            badge=badge,
            volunteer=volunteer,
        )
    return volunteer_admin(request, success="Badge assigned to volunteer")

def remove_badge_from_volunteer(request, volunteer_id, badge_id):
    badge = Badge.objects.get(id=badge_id)
    if not check_ownership(request, badge):
        return volunteer_admin(request, error="You do not have permission to remove this badge")
    volunteer = Volunteer.objects.get(id=volunteer_id)
    VolunteerBadge.objects.get(badge=badge, volunteer=volunteer).delete()
    return volunteer_admin(request, success="Badge removed from volunteer")

def manage_badge_opportunity(request, badge_id, opportunity_id, delete=False):
    badge = Badge.objects.get(id=badge_id)
    opportunity = Opportunity.objects.get(id=opportunity_id)
    if not check_ownership(request, badge):
        return opportunity_admin(request, error="You do not have permission to assign this badge")
    if not check_ownership(request, opportunity):
        return opportunity_admin(request, error="You do not have permission to assign this badge")
    if delete:
        BadgeOpporunity.objects.get(badge=badge, opportunity=opportunity).delete()
        return opportunity_admin(request, success="Badge removed from opportunity")
    if BadgeOpporunity.objects.filter(badge=badge, opportunity=opportunity).exists():
        return opportunity_admin(request, error="Badge already assigned to opportunity")
    BadgeOpporunity.objects.create(
        badge=badge,
        opportunity=opportunity,
    )
    return opportunity_admin(request, success="Badge assigned to opportunity")
        
    
    
    

##system transfer

def export_all_orgs_zip(request):
    #create a zip file, with folder for each org
    #each folder will have the media ascociated with it and a csv of the data
    
    if not request.user.is_superuser:
        return HttpResponse("You do not have permission to export data")
    
    orgs = Organisation.objects.all()


    export_path = "/home/fab/export/"#
    
        
    
    os.system("rm -r /home/fab/export/*")
    
    icons = Icon.objects.all()
    icons_list = []
    for icon in icons:
        icon_l = {
            "name": icon.name,
            "url": icon.icon.url.split("/")[-1],
        }
        os.system("cp \"{}\" \"{}\"".format("/home/fab/volunteering-system/src/" + icon.icon.url, export_path))
        
        icons_list.append(icon_l)
    
    with open(export_path + "icons.csv", "w") as f:
        writer = csv.writer(f)
        for icon in icons_list:
            for key, value in icon.items():
                writer.writerow([key, value])
        f.close()
        
    link_types = LinkType.objects.all()
    link_types_list = []
    os.mkdir(export_path + 'links')
    
    for link_type in link_types:
        link_type_l = {
            "name": link_type.name,
            "icon": link_type.icon.url.split("/")[-1],
        }
        os.system("cp \"{}\" \"{}\"".format("/home/fab/volunteering-system/src/" + link_type.icon.url, export_path + "links"))
        
        link_types_list.append(link_type_l)
    
    with open(export_path + "link_types.csv", "w") as f:
        writer = csv.writer(f)
        header = link_types_list[0].keys()
        writer.writerow(header)
        for link_type in link_types_list:
            writer.writerow(link_type.values())
    
    for org in orgs:
        
        os.mkdir(export_path + org.name)
        os.mkdir(export_path + org.name + "/media")
        os.mkdir(export_path + org.name + "/media_thumbnail")
        
        print("Exporting {}".format(org.name))
        
        org_images = OrgImage.objects.filter(organisation=org)
        org_videos = OrgVideo.objects.filter(organisation=org)
        org_locations = Location.objects.filter(organisation=org)
        org_links = Link.objects.filter(organisation=org)
        
        org_opportunities = Opportunity.objects.filter(organisation=org)
        #print('oppotunities', opportunities)
        opp_locations = OppLocation.objects.filter(opportunity__in=org_opportunities)
        
        print("Data count: \n Org: {} \n Org Images: {} \n Org Videos: {} \n Org Locations: {} \n Opportunities: {} \n Opp Locations: {}".format(
            org, 
            len(org_images), 
            len(org_videos), 
            len(org_locations), 
            len(org_opportunities), 
            len(opp_locations)))
        
        print("packaging data")
        
        org_data = {
            "name": org.name,
            "description": org.description,
            "logo": org.logo.url.split("/")[-1] if org.logo else None,
            "featured": org.featured,
        }
        
        org_links_list = []
        
        for link in org_links:
            if link.link_type == None:
                continue
            org_links_list.append({
                "url": link.url,
                "type": link.link_type.name,
            })
        
        org_locations_l = []
        
        for location in org_locations:
            org_locations_l.append({
                "name": location.name,
                "address": location.address,
                "place_id": location.place_id,
                "longitude": location.longitude,
                "latitude": location.latitude,
            })
            
        opp_locations_l = []
        
        for location in opp_locations:
            opp_locations_l.append({
                "opportunity": location.opportunity.name,
                "name": location.name,
                "address": location.address,
                "place_id": location.place_id,
                "longitude": location.longitude,
                "latitude": location.latitude,
            })
            
        org_media = []
        
        for image in org_images:
            org_media.append({
                "type": "image",
                "url": image.image.url.split("/")[-1],
                "thumbnail": image.thumbnail_image.url.split("/")[-1] if image.thumbnail_image else ""
            })
            
        for video in org_videos:
            org_media.append({
                "type": "video",
                "url": video.video.url.split("/")[-1],
                "thumbnail": video.video_thumbnail.url.split("/")[-1] if video.video_thumbnail else ""
            })
            
            
        opp_media = []
        
        for image in OppImage.objects.filter(opportunity__in=org_opportunities):
            opp_media.append({
                "opportunity": image.opportunity.name,
                "type": "image",
                "url": image.image.url.split("/")[-1],
                "thumbnail": image.thumbnail_image.url.split("/")[-1] if image.thumbnail_image else ""
            })
            
            os.system("cp \"{}\" \"{}\"".format("/home/fab/volunteering-system/src/" + image.image.url, export_path + org.name + "/media")) if image.image else None
            os.system("cp \"{}\" \"{}\"".format("/home/fab/volunteering-system/src/" + image.thumbnail_image.url, export_path + org.name + "/media_thumbnail")) if image.thumbnail_image else None
        for video in OppVideo.objects.filter(opportunity__in=org_opportunities):
            opp_media.append({
                "type": "video",
                "url": video.video.url.split("/")[-1],
                "thumbnail": video.video_thumbnail.url.split("/")[-1] if video.video_thumbnail else ""
            })
            
            os.system("cp \"{}\" \"{}\"".format("/home/fab/volunteering-system/src/" + video.video.url, export_path + org.name + "/media")) if video.video else None
            os.system("cp \"{}\" \"{}\"".format("/home/fab/volunteering-system/src/" + video.video_thumbnail.url, export_path + org.name + "/media_thumbnail")) if video.video_thumbnail else None
        opportunities = []
        
        for opportunity in org_opportunities:
            opportunities.append({
                "name": opportunity.name,
                "description": opportunity.description,
                "start_time": opportunity.start_time,
                "end_time": opportunity.end_time,
                "recurrences": opportunity.recurrences,
                "featured": opportunity.featured,
                "benefits": [benefit.description for benefit in Benefit.objects.filter(opportunity=opportunity)],
                "benefit_icons": [benefit.icon.icon.url.split("/")[-1] for benefit in Benefit.objects.filter(opportunity=opportunity)],
                "tags":[tag.tag.tag for tag in LinkedTags.objects.filter(opportunity=opportunity)]
            })
            
        print("Saving Data")
        #create a folder for the org
        
        #create a seperate csv for each type
        

        with open(export_path + org.name + "/organisation.csv".format(org.name), "w") as f:
            writer = csv.writer(f)
            header = org_data.keys()
            writer.writerow(header)
            writer.writerow(org_data.values())
            f.close()
            
        os.system("cp \"{}\" \"{}\"".format("/home/fab/volunteering-system/src/" + org.logo.url, export_path + org.name)) if org.logo else None
            
        if len(org_locations_l) > 0:
            with open(export_path + org.name + "/locations.csv", "w") as f:
                writer = csv.writer(f)
                header = org_locations_l[0].keys()
                writer.writerow(header)
                for location in org_locations_l:
                    writer.writerow(location.values())
                f.close()
        else:
            print ("no locations", org.name)
                
        if len(opp_locations_l) > 0:
            with open(export_path + org.name + "/opportunity_locations.csv", "w") as f:
                writer = csv.writer(f)
                header = opp_locations_l[0].keys()
                writer.writerow(header)
                for location in opp_locations_l:
                    writer.writerow(location.values())
                f.close()
        else:
            print ("no opp locations", org.name)
        
        if len(org_media) > 0:
            with open(export_path + org.name + "/media.csv", "w") as f:
                writer = csv.writer(f)
                header = org_media[0].keys()
                writer.writerow(header)
                for media in org_media:
                    writer.writerow(media.values())
                f.close()
                
        if len(opportunities) > 0:
            with open(export_path + org.name + "/opportunities.csv", "w") as f:
                writer = csv.writer(f)
                header = opportunities[0].keys()
                writer.writerow(header)
                for opportunity in opportunities:
                    writer.writerow(opportunity.values())
                    
                f.close()
                
        if len(opp_media) > 0:
            with open(export_path + org.name + "/opportunity_media.csv", "w") as f:
                writer = csv.writer(f)
                header = opp_media[0].keys()
                writer.writerow(header)
                for media in opp_media:
                    writer.writerow(media.values())
                f.close()
                
        if len(org_links_list) > 0:
            with open(export_path + org.name + "/links.csv", "w") as f:
                writer = csv.writer(f)
                header = org_links_list[0].keys()
                writer.writerow(header)
                for link in org_links_list:
                    writer.writerow(link.values())
                f.close()

        #add the media to the folder

        for image in org_images:
            os.system("cp \"{}\" \"{}\"".format("/home/fab/volunteering-system/src/" + image.image.url, export_path + org.name + "/media"))
            if image.thumbnail_image:
                os.system("cp \"{}\" \"{}\"".format("/home/fab/volunteering-system/src/" + image.thumbnail_image.url, export_path + org.name + "/media_thumbnail"))
        
        for video in org_videos:
            os.system("cp \"{}\" \"{}\"".format("/home/fab/volunteering-system/src/" + video.video.url, export_path + org.name + "/media"))
            if video.video_thumbnail:
                os.system("cp \"{}\" \"{}\"".format("/home/fab/volunteering-system/src/" + video.video_thumbnail.url, export_path + org.name + "/media_thumbnail"))
        

    
    os.system("zip -r /home/fab/export/export.zip /home/fab/export/")
    
    response = HttpResponse(open("/home/fab/export/export.zip", "rb"), content_type="application/zip")
    response["Content-Disposition"] = "attachment; filename=export.zip"
    return response