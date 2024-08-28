from django.shortcuts import render
from commonui.views import check_if_hx, HTTPResponseHXRedirect
from .common import check_ownership
from ..models import OrganisationAdmin
from opportunities.models import Opportunity, Location, Image, Video, OpportunityView, Registration, Benefit, Icon, OpportunityBenefit
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
            "benefits": OpportunityBenefit.objects.filter(opportunity=opp),
        }
        
        return render(request, "org_admin/partials/opportunity_benefits.html", context=context)
    
