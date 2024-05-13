from django.shortcuts import render
from django.http import HttpResponse 
from ..models import OrganisationAdmin
from commonui.views import check_if_hx, HTTPResponseHXRedirect
from webpush import  send_user_notification
from organisations.models import Location, Video as OrgVideo, Image as OrgImage, Link, LinkType, Organisation
from opportunities.models import Opportunity, Image as OppImage, Video as OppVideo, Registration, OpportunityView, Location as OppLocation
from communications.models import Message, Chat
from opportunities.models import Opportunity, Image as OppImage, Video as OppVideo, Registration, OpportunityView, SupplimentaryInfoRequirement, VolunteerRegistrationStatus, RegistrationAbsence, RegistrationStatus, Icon
from volunteer.models import Volunteer, VolunteerConditions, VolunteerSupplementaryInfo, SupplementaryInfo
from .common import check_ownership
from datetime import datetime, timedelta, date
import requests
from requests_oauthlib import OAuth1
from django.conf import settings
import json

# Create your views here.
def volunteer_admin(request):
    #List of volunteers without repeating
    if request.user.is_superuser:
        volunteers = Volunteer.objects.all()
        context = {
            "hx": check_if_hx(request),
            "unique_volunteers": volunteers,
        }
        
    else:
        registrations = Registration.objects.filter(opportunity__organisation=OrganisationAdmin.objects.get(user=request.user).organisation)
        unique_volunteers = Volunteer.objects.filter(id__in=registrations.values_list('volunteer', flat=True)).distinct()
        print(unique_volunteers)
        context = {
            "hx": check_if_hx(request),
            "unique_volunteers": unique_volunteers,
        }
        
    return render(request, "org_admin/volunteer_admin.html", context)



def opportunity_admin(request):
    
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
         
         },
    )


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


def details(request, error=None, success=None, organisation_id=None):
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
            return render(request, "org_admin/no_admin.html", {"hx": check_if_hx(request)})

        org_videos = OrgVideo.objects.filter(organisation=organisation)
        org_images = OrgImage.objects.filter(organisation=organisation)
        
        link_types = LinkType.objects.all()
        
        supp_info = SupplementaryInfo.objects.filter(organisation=organisation)
        
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
            "link_types": link_obj,
            "supp_info": supp_info,
            "locations": Location.objects.filter(organisation=organisation),
            "error": error,
            "success": success,
            "superuser": request.user.is_superuser,
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
    
    context = {
        "hx": check_if_hx(request),
        "volunteer": volunteer,
        "registrations": registrations,
        "conditions": conditions,
        "vol_supp_info": vol_supp_info,
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
        