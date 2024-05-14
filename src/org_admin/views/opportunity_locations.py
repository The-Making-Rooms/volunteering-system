from django.shortcuts import render
from commonui.views import check_if_hx, HTTPResponseHXRedirect
from .common import check_ownership
from ..models import OrganisationAdmin
from opportunities.models import Opportunity, Image, Video, OpportunityView, Registration, Location as OppLocation
from organisations.models import Location as OrgLocation, Organisation
from .opportunity_details import opportunity_details
from .views import details
from googlemaps import Client as GoogleMaps


def opportunity_locations(request, id):
    if request.method == "GET":
        
        opportunity = Opportunity.objects.get(id=id)
        locations = OppLocation.objects.filter(opportunity=opportunity)
        
        context = {
            "hx": check_if_hx(request),
            "locations": locations,
            "opportunity": opportunity,
        }
        
        return render(request, "org_admin/partials/opportunity_locations.html", context=context)

def add_location_by_id(request, opportunity_id=None, organisation_id=None):
    if request.method == "POST":
        data = request.POST
        if opportunity_id:
            if OppLocation.objects.filter(place_id=data["location_id"], opportunity=Opportunity.objects.get(id=opportunity_id)).exists():
                request.method = "GET"
                return opportunity_details(request, opportunity_id, error="Location already exists", tab_name="locations")
            OppLocation.objects.create(
                opportunity=Opportunity.objects.get(id=opportunity_id),
                name=data["location_name"],
                address=data["location_address"],
                place_id=data["location_id"],
                longitude=data["longitude"],
                latitude=data["latitude"],
                ).save()
            request.method = "GET"
            return opportunity_details(request, opportunity_id, success="Location added", tab_name="locations")
        else:
            if request.user.is_superuser and organisation_id:
                organisation = Organisation.objects.get(id=organisation_id)
            elif request.user.is_superuser:
                return details(request, error="Organisation not found")
            else:
                organisation = OrganisationAdmin.objects.get(user=request.user).organisation
                
            if OrgLocation.objects.filter(place_id=data["location_id"]).exists():
                request.method = "GET"
                return details(request, organisation_id=organisation_id, error="Location already exists")
            OrgLocation.objects.create(
                organisation= organisation,
                name=data["location_name"],
                address=data["location_address"],
                place_id=data["location_id"],
                longitude=data["longitude"],
                latitude=data["latitude"],
                ).save()
            request.method = "GET"
            return details(request, organisation_id=organisation_id,success="Location added")
    
def delete_org_location(request, location_id):
    try:
        if check_ownership(request, OrgLocation.objects.get(id=location_id)):
            location = OrgLocation.objects.get(id=location_id)
            organisation_id = location.organisation.id
            location.delete()
            return details(request, organisation_id=organisation_id, success="Location deleted")
        else:
            return details(request, error="You do not have permission to delete this location", tab_name="locations")
    except Exception as e:
        return details(request, error=e)
    
def delete_opportunity_location(request, location_id):
    try:
        if check_ownership(request, OppLocation.objects.get(id=location_id)):
            location = OppLocation.objects.get(id=location_id)
            location.delete()
            return opportunity_details(request, location.opportunity.id, success="Location deleted", tab_name="locations")
        else:
            return opportunity_details(request, location.opportunity.id, error="You do not have permission to delete this location", tab_name="locations")
    except Exception as e:
        return opportunity_details(request, location.opportunity.id, error=e)

#Now only used to delete things.
def manage_opportunity_location(request, opportunity_id, location_id=None, delete=False):
        location = None
        if location_id != None:
            try:
                location = OppLocation.objects.get(id=location_id)
                if delete:
                    try:
                        location.delete()
                        request.method = "GET"
                        return opportunity_details(request, opportunity_id, success="Location deleted", tab_name="locations")
                    except Exception as e:
                        request.method = "GET"
                        return opportunity_details(request, opportunity_id, error=e, tab_name="locations")
            except OppLocation.DoesNotExist:
                return opportunity_details(request, opportunity_id, error="Location does not exist", tab_name="locations")
