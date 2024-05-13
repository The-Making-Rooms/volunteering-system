from django.shortcuts import render
from commonui.views import check_if_hx, HTTPResponseHXRedirect
from .common import check_ownership
from ..models import OrganisationAdmin
from opportunities.models import Opportunity, Location, Image, Video, OpportunityView, Registration, Benefit, Icon
from .opportunity_details import opportunity_admin_list, opportunity_details
import requests
from requests_oauthlib import OAuth1
from django.conf import settings
from io import BytesIO
from django.core.files.base import ContentFile


def opportunity_benefits(request, id):
    if request.method == "GET":
        if not check_ownership(request, Opportunity.objects.get(id=id)):
            return opportunity_admin_list(request, error="You do not have permission to view this opportunity")

        try:
            opp = Opportunity.objects.get(id=id)
        except Opportunity.DoesNotExist:
            return opportunity_admin_list(request, error="Opportunity does not exist")
        
        context = {
            "hx": check_if_hx(request),
            "opportunity": opp,
            "benefits": Benefit.objects.filter(opportunity=opp),
        }
        
        return render(request, "org_admin/partials/opportunity_benefits.html", context=context)
    
def manage_benefit(request, opportunity_id=None, benefit_id=None, delete=False):
    if request.method == "GET":
        if opportunity_id:
            opportunity = Opportunity.objects.get(id=opportunity_id)
            if check_ownership(request, opportunity): 

                return render(request, "org_admin/partials/add_benefit.html", context={"hx": check_if_hx(request), "opportunity": opportunity})
            return opportunity_admin_list(request, error="You do not have permission to view this opportunity")
        if benefit_id:
            if delete:
                benefit = Benefit.objects.get(id=benefit_id)
                opportunity_id = benefit.opportunity.id
                benefit.delete()
                return opportunity_details(request, opportunity_id, tab_name="benefits")
            benefit = Benefit.objects.get(id=benefit_id)
            return render(request, "org_admin/partials/add_benefit.html", context={"hx": check_if_hx(request), "benefit": benefit})
        
    if request.method == "POST":
        if opportunity_id:
            opportunity = Opportunity.objects.get(id=opportunity_id)
            if check_ownership(request, opportunity):
                
                benefit = Benefit.objects.create(
                    opportunity=opportunity,
                    description=request.POST.get("description"),
                )
                
                print(request.POST)
                
                if request.POST.get("icon"):
                    print("icon")
                    add_icon(benefit, request.POST.get("icon"))       
                    
                
                request.method = "GET"
                return opportunity_details(request, opportunity_id, tab_name="benefits")
            return opportunity_admin_list(request, error="You do not have permission to view this opportunity")
        if benefit_id:
            benefit = Benefit.objects.get(id=benefit_id)
            benefit.description = request.POST.get("description")
            
            print(request.POST)
            
            if request.POST.get("icon"):
                add_icon(benefit, request.POST.get("icon"))
                
            benefit.save()
            request.method = "GET"
            return opportunity_details(request, benefit.opportunity.id, tab_name="benefits")
        

def add_icon(benefit, icon_id):

    auth = OAuth1(settings.NOUN_PROJECT_API_KEY, settings.NOUN_PROJECT_SECRET_KEY)
    endpoint = "https://static.thenounproject.com/png/{}-200.png"
    

    #download file into bytesIO
    img_bytes = requests.get(endpoint.format(icon_id), auth=auth).content
    
    bytes_io = BytesIO(img_bytes)

    icon = Icon.objects.create()
    
    icon.icon.save("{}.png".format(icon_id), ContentFile(bytes_io.getvalue()))
    icon.save()
   
    benefit.icon = icon
        
    benefit.save()