from django.shortcuts import render

from org_admin.forms import OrganisationLocationForm, OpportunityLocationForm
from .models import OrgnaisationAdmin
from commonui.views import check_if_hx, HTTPResponseHXRedirect
from django.forms import formset_factory
from webpush import send_group_notification
from organisations.models import Location, Video as OrgVideo, Image as OrgImage
from opportunities.models import Opportunity, Image as OppImage, Video as OppVideo, Registration, OpportunityView, Location as OppLocation
from communications.models import Message
from django.urls import reverse_lazy
import datetime
from opportunities.models import Opportunity, Image as OppImage, Video as OppVideo, Registration, OpportunityView
from volunteer.models import Volunteer

import recurrence

# Create your views here.
def index(request, error=None):
    try:
        orgnaisation = OrgnaisationAdmin.objects.get(user=request.user)
    except OrgnaisationAdmin.DoesNotExist:
        return render(request, "org_admin/no_admin.html", {"hx": check_if_hx(request)})
    
    total_volunteers = Registration.objects.filter(opportunity__organisation=orgnaisation.organisation).count()
    #past 24 hours views
    total_views = OpportunityView.objects.filter(opportunity__organisation=orgnaisation.organisation, time__gte=datetime.datetime.now()-datetime.timedelta(days=1)).count()
    #past 24 hours mesages
    messages = Message.objects.filter(chat__organisation=orgnaisation.organisation, timestamp__gte=datetime.datetime.now()-datetime.timedelta(days=1)).count()

    return render(
        request,
        "org_admin/index.html",
        {
            "hx": check_if_hx(request),
            "error": error,
            "organisation": orgnaisation.organisation,
            "total_volunteers": total_volunteers,
            "total_views": total_views,
            "messages": messages,


        },
    )

def volunteer_admin(request):
    #List of volunteers without repeating
    registrations = Registration.objects.filter(opportunity__organisation=OrgnaisationAdmin.objects.get(user=request.user).organisation)
    unique_volunteers = Volunteer.objects.filter(id__in=registrations.values_list('volunteer', flat=True)).distinct()
    print(unique_volunteers)
    context = {
        "hx": check_if_hx(request),
        "unique_volunteers": unique_volunteers,
    }
    return render(request, "org_admin/volunteer_admin.html", context)


def check_ownership(request, entity):
    try:
        if (
            entity.organisation
            != OrgnaisationAdmin.objects.get(user=request.user).organisation
        ):
            return False
        else:
            return True
    except AttributeError:
        if entity.opportunity.organisation != OrgnaisationAdmin.objects.get(
            user=request.user
        ).organisation:
            return False
        else:
            return True

def opportunity_details_admin(request, id, error=None):
    if request.method == "POST":
        data = request.POST
        if not check_ownership(request, Opportunity.objects.get(id=id)):
            return opportunity_details(request, id, error="You do not have permission to edit this opportunity")
    
        start_date = datetime.datetime.strptime(data["start_date"], "%Y-%m-%d")
        end_date = datetime.datetime.strptime(data["end_date"], "%Y-%m-%d")
        
        start_time = datetime.datetime.strptime(data["start_time"], "%H:%M")
        end_time = datetime.datetime.strptime(data["end_time"], "%H:%M")
        
        if start_date > end_date:
            return opportunity_details(request, id, error="Start date must be before end date")
        
        if start_time > end_time:
            return opportunity_details(request, id, error="Start time must be before end time")
        
        opp = Opportunity.objects.get(id=id)
        opp.name = data["name"]
        opp.description = data["description"]
        opp.recurrences.dtstart = start_date
        opp.recurrences.dtend = end_date
        opp.start_time = start_time
        opp.end_time = end_time
        
        try:
            if data["active"] == "on":
                opp.active = True
            else:
                opp.active = False
        except KeyError:
            opp.active = False
        
        try:
            if data["featured"] == "on":
                opp.featured = True
            else:
                opp.featured = False
        except KeyError:
            opp.featured = False

            
        if data["recurrences"] == "never":
            opp.recurrences.rrules = []
        elif data["recurrences"] == "daily":
            opp.recurrences.rrules = [recurrence.Rule(recurrence.DAILY)]
        elif data["recurrences"] == "weekly":
            day_name = start_date.strftime("%w")
            opp.recurrences.rrules = [recurrence.Rule(recurrence.WEEKLY, byday=[int(day_name)-1])]
            
        elif data["recurrences"] == "monthly":
            opp.recurrences.rrules = [recurrence.Rule(recurrence.MONTHLY)]
        elif data["recurrences"] == "yearly":
            opp.recurrences.rrules = [recurrence.Rule(recurrence.YEARLY)]
            
        
        opp.save()
        
            
        return opportunity_details(request, id, error, success="Opportunity updated successfully")
    else:
        return opportunity_details(request, id, error)

def opportunity_details(request, id, error=None, success=None):
    try:
        opp = Opportunity.objects.get(id=id)
    except Opportunity.DoesNotExist:
        return index(request, error="Opportunity does not exist")
    
    
    try:
        reccurances = opp.recurrences.rrules[0].freq
        start_date = opp.recurrences.dtstart
        end_date = opp.recurrences.dtend
    except IndexError:
        reccurances = 'none'
        start_date = None
        end_date = None
        
        
    individual_dates = opp.recurrences.rdates


    opp_images = OppImage.objects.filter(opportunity=opp)
    opp_videos = OppVideo.objects.filter(opportunity=opp)
    
    
    context = {
        "hx": check_if_hx(request),
        "opportunity": opp,
        "recurrences": reccurances,
        "start_date": start_date,
        "end_date": end_date,
        "opp_images": opp_images,
        "opp_videos": opp_videos,
        "individual_dates": individual_dates,
        "success": success,
        "error": error,
    }
    

    return render(
        request,
        "org_admin/opportunity_details_admin.html",
        context=context,
    )
    
def delete_date(request, id, opportunity_id):
    opp = Opportunity.objects.get(id=opportunity_id)
    if check_ownership(request, opp):
        opp.recurrences.rdates.remove(opp.recurrences.rdates[id])
        opp.save()
    else:
        return opportunity_details(request, opportunity_id, error="You do not have permission to delete this date")
    
    return HTTPResponseHXRedirect(reverse_lazy("opportunity_details", args=[opportunity_id]))

def add_date(request, id):
    if request.method == "POST":
        data = request.POST
        opp = Opportunity.objects.get(id=id)
        if check_ownership(request, opp):
            opp.recurrences.rdates.append(datetime.datetime.strptime(data["date"], "%Y-%m-%d"))
            opp.save()
        else:
            return opportunity_details(request, id, error="You do not have permission to add a date")
        
        return HTTPResponseHXRedirect(reverse_lazy("opportunity_details", args=[id]))
    else:
        return render(
            request,
            "org_admin/partials/add_date.html",
            {"hx": check_if_hx(request), "opportunity_id": id},
        )

def opportunity_admin(request):
    opportunities = Opportunity.objects.filter(
        organisation=OrgnaisationAdmin.objects.get(user=request.user).organisation
    )

    []

    for opportunity in opportunities:
        opportunity.registrations = Registration.objects.filter(opportunity=opportunity).count()
        opportunity.views = OpportunityView.objects.filter(opportunity=opportunity).count()
        

    return render(
        request,
        "org_admin/opportunity_admin.html",
        {"hx": check_if_hx(request), "opportunities": opportunities},
    )


def delete_media(request, id, location, media_type):

    if media_type == "image" and location == "org_media":
        media = OrgImage.objects.get(id=id)
    elif media_type == "video" and location == "org_media":
        media = OrgVideo.objects.get(id=id)
    elif media_type == "image" and location == "opportunity_media":
        media = OppImage.objects.get(id=id)
    elif media_type == "video" and location == "opportunity_media":
        media = OppVideo.objects.get(id=id)
    else:
        return details(request, error="Media type not found")
    
    if check_ownership(request, media):
        media.delete()
    else:
        return details(
            request, error="You do not have permission to delete this media"
        )

    if location == "org_media":
        return HTTPResponseHXRedirect(reverse_lazy("details"))
    elif location == "opportunity_media":
        return HTTPResponseHXRedirect(
            reverse_lazy("opportunity_details", args=[media.opportunity.id])
        )


def upload_media(request, location, id=None):
    if request.method == "GET":
        if location == "org_media":
            url = reverse_lazy("upload_media_organisation")
        elif location == "opportunity_media":
            url = reverse_lazy("upload_media_opportunity", args=[id])

        return render(
            request,
            "org_admin/partials/file_upload.html",
            {"hx": check_if_hx(request), "upload_url": url},
        )

    elif request.method == "POST":
        data = request.POST
        file = request.FILES["file"]
        file_type = file.content_type.split("/")[1]

        # emergency_contact = emergency_contact_form.save(commit=False)
        # emergency_contact.volunteer = volunteer
        try:
            if file_type == "jpeg":
                if location == "org_media":
                    OrgImage.objects.create(
                        image=file,
                        organisation=OrgnaisationAdmin.objects.get(
                            user=request.user
                        ).organisation,
                    )
                elif location == "opportunity_media":
                    OppImage.objects.create(
                        image=file,
                        opportunity=Opportunity.objects.get(id=id),
                    )
            elif file_type == "mp4":
                if location == "org_media":
                    OrgVideo.objects.create(
                        video=file,
                        organisation=OrgnaisationAdmin.objects.get(
                            user=request.user
                        ).organisation,
                    )
                elif location == "opportunity_media":
                    OppVideo.objects.create(
                        video=file,
                        opportunity=Opportunity.objects.get(id=id),
                    )

            if location == "org_media":
                return HTTPResponseHXRedirect(reverse_lazy("details"))
            elif location == "opportunity_media":
                return HTTPResponseHXRedirect(
                    reverse_lazy("opportunity_details", args=[id])
                )
        except Exception as e:
            print(e)
            if location == "org_media":
                return details(request, error=e)
            elif location == "opportunity_media":
                return opportunity_details(request, id, error=e)


def opportunity_location(request, opportunity_id, location_id, delete=False):
    if request.method == "POST":
        data = request.POST
        if location_id != "":
            location = OppLocation.objects.get(id=location_id)
            if not check_ownership(request, location):
                return opportunity_details(
                    request, opportunity_id, error="You do not have permission to edit this location"
                )
            else:
                form = OpportunityLocationForm(data, instance=location)
                if form.is_valid():
                    form.save()
                    return opportunity_details(request, opportunity_id)
                else:
                    return opportunity_details(request, opportunity_id, error=form.errors)
        else:
            form = OpportunityLocationForm(data)
            if form.is_valid():
                form.save()
                return opportunity_details(request, opportunity_id)
            else:
                return opportunity_details(request, opportunity_id, error=form.errors)

    if location_id != None:
        try:
            location = OppLocation.objects.get(id=location_id)
        except OppLocation.DoesNotExist:
            return opportunity_details(request, opportunity_id, error="Location does not exist")

        if delete:
            try:
                location.delete()
                return opportunity_details(request, opportunity_id)
            except Exception as e:
                return opportunity_details(request, opportunity_id, error=e)
        else:
            return render(
                request,
                "org_admin/partials/add_location.html",
                {
                    "hx": check_if_hx(request),
                    "location": location,
                    "opportunity_id": opportunity_id,
                },
            )
    else:
        return render(
            request,
            "org_admin/partials/add_location.html",
            {
                "hx": check_if_hx(request),
                "opportunity_id": opportunity_id,
            },
        )
# Location crud views
def location(request, id=None, delete=False):
    if request.method == "POST":
        print(request.POST)
        data = request.POST

        if data["locationID"] != "":
   
            location = Location.objects.get(id=data["locationID"])

            
            if not check_ownership(request, location):
                return details(
                    request, error="You do not have permission to edit this location"
                )
            else:
                form = OrganisationLocationForm(data, instance=location)
                if form.is_valid():
                    form.save()
                    return details(request)
                else:
                    return details(request, error=form.errors)
        else:
            form = OrganisationLocationForm(data)
            if form.is_valid():
                form.save()
                return details(request)
            else:
                return details(request, error=form.errors)

    if id != None:
        try:
            location = Location.objects.get(id=id)
        except Location.DoesNotExist:
            return details(request, error="Location does not exist")

        if delete:
            try:
                location.delete()
                return details(request)
            except Exception as e:
                return details(request, error=e)
        else:
            return render(
                request,
                "org_admin/partials/add_location.html",
                {
                    "hx": check_if_hx(request),
                    "location": location,
                    "org_id": OrgnaisationAdmin.objects.get(
                        user=request.user
                    ).organisation.id,
                },
            )
    else:
        return render(
            request,
            "org_admin/partials/add_location.html",
            {
                "hx": check_if_hx(request),
                "org_id": OrgnaisationAdmin.objects.get(
                    user=request.user
                ).organisation.id,
            },
        )
        


def details(request, error=None):
    try:
        orgnaisation = OrgnaisationAdmin.objects.get(user=request.user)
    except OrgnaisationAdmin.DoesNotExist:
        return render(request, "org_admin/no_admin.html", {"hx": check_if_hx(request)})

    org_videos = OrgVideo.objects.filter(organisation=orgnaisation.organisation)
    org_images = OrgImage.objects.filter(organisation=orgnaisation.organisation)

    context = {
        "hx": check_if_hx(request),
        "locations": Location.objects.filter(organisation=orgnaisation.organisation),
        "organisation": orgnaisation.organisation,
        "org_videos": org_videos,
        "org_images": org_images,
        "error": error,
    }

    return render(request, "org_admin/organisation_details_admin.html", context)
