from django.shortcuts import render
from ..models import OrganisationAdmin
from commonui.views import check_if_hx, HTTPResponseHXRedirect
from webpush import  send_user_notification
from organisations.models import Location, Video as OrgVideo, Image as OrgImage, Link, LinkType, Organisation
from opportunities.models import Opportunity, Image as OppImage, Video as OppVideo, Registration, OpportunityView, Location as OppLocation
from communications.models import Message, Chat
from opportunities.models import Opportunity, Image as OppImage, Video as OppVideo, Registration, OpportunityView, SupplimentaryInfoRequirement
from volunteer.models import Volunteer, VolunteerConditions, VolunteerSupplementaryInfo
from .common import check_ownership


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
            "locations": Location.objects.filter(organisation=organisation),
            "error": error,
            "success": success,
            "superuser": request.user.is_superuser,
        }

        return render(request, "org_admin/organisation_details_admin.html", context)

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
    