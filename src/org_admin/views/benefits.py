from django.shortcuts import render
from django.http import HttpResponse
from opportunities.models import Opportunity, Benefit, OpportunityBenefit
from organisations.models import Organisation, OrganisationAdmin
from commonui.views import check_if_hx, HTTPResponseHXRedirect
from .common import check_ownership
from django.conf import settings
from io import BytesIO
from django.core.files.base import ContentFile
from opportunities.models import Icon
from requests_oauthlib import OAuth1
import requests
from .opportunity_details import opportunity_admin_list, opportunity_details


def convert_old_schema(request):
    benefits = Benefit.objects.all()
    
    for benefit in benefits:
        print(benefit)
        try:
            OpportunityBenefit.objects.get(benefit=benefit)
        except OpportunityBenefit.DoesNotExist:
            NewOpportunityBenefit = OpportunityBenefit.objects.create(
                opportunity=benefit.opportunity,
                benefit=benefit
            )
            NewOpportunityBenefit.save()
        
    for benefit in benefits:
        benefit.orgnaisation = benefit.opportunity.organisation
        print(benefit, benefit.organisation)
        benefit.save()
        
    return HttpResponse("Done")
        
    
def benefits_index(request, error=None, success=None):
    if request.user.is_superuser:
        benefits = Benefit.objects.all()
    else:
        benefits = Benefit.objects.filter(organisation=OrganisationAdmin.objects.get(user=request.user).organisation)
    
    context = {
        'benefits': benefits,
        'hx': check_if_hx(request),
        'error': error,
        'success': success
    }
    
    return render(request, 'org_admin/benefits.html', context)
        

def add_benefit(request, opportunity_id=None):
    post_data = request.POST
    
    print(post_data)
    
    if request.method == "POST":
        benefit = Benefit.objects.create(
            description=post_data.get("description"),
            organisation= Organisation.objects.get(id=post_data.get("organisation")) if request.user.is_superuser else OrganisationAdmin.objects.get(user=request.user).organisation
        )
        print("post_data")
        
        if post_data.get("icon"):
            add_icon(benefit, post_data.get("icon"))
            
    
            
        if post_data.get("opportunity_id"):
            
            OpportunityBenefit.objects.create(
                opportunity=Opportunity.objects.get(id=post_data.get("opportunity_id")),
                benefit=benefit
            )
            
            request.method = "GET"
            return opportunity_details(request, post_data.get("opportunity_id"), tab_name="benefits", success="Benefit has been added to the opportunity")
        
        return HTTPResponseHXRedirect("/org_admin/benefits/")

    else:
        
        context = {
            "hx": check_if_hx(request),
            "organisations" : Organisation.objects.all() if request.user.is_superuser else [OrganisationAdmin.objects.get(user=request.user).organisation],
            "superuser": request.user.is_superuser,
            "opportunity_id": opportunity_id
        }
        
        
        return render(request, "org_admin/partials/add_benefit.html", context=context)

def benefit_crud(request, benefit_id=None, opportunity_id=None):
    if request.method == "GET":
        if benefit_id:
            benefit = Benefit.objects.get(id=benefit_id)
            context = {
                "hx": check_if_hx(request),
                "benefit": benefit,
                "organisations" : Organisation.objects.all() if request.user.is_superuser else [OrganisationAdmin.objects.get(user=request.user).organisation],
                "superuser": request.user.is_superuser,
                "opportunity_id": opportunity_id
            }
            return render(request, "org_admin/partials/add_benefit.html", context=context)
        return render(request, "org_admin/partials/add_benefit.html", context={"hx": check_if_hx(request)})
    
    if request.method == "POST":
        if benefit_id:
            benefit = Benefit.objects.get(id=benefit_id)
            benefit.description = request.POST.get("description")
            benefit.save()
            
            if request.POST.get("icon"):
                add_icon(benefit, request.POST.get("icon"))
                
            if request.POST.get("opportunity_id"):
                request.method = "GET"                
                return opportunity_details(request, request.POST.get("opportunity_id"), tab_name="benefits", success="Benefit has been updated")
            
            
            return HTTPResponseHXRedirect("/org_admin/benefits/")
        else:
            return add_benefit(request)
        
def delete_benefit(request, benefit_id):
    benefit = Benefit.objects.get(id=benefit_id)
    benefit.delete()
    return benefits_index(request)

def select_opportunity(request):
    post_data = request.POST
    
    organisation = Benefit.objects.get(id=post_data.getlist("benefit")[0]).organisation if request.user.is_superuser else OrganisationAdmin.objects.get(user=request.user).organisation
    
    print(post_data.getlist("benefit"))
    
    #Get the unique organisations of the benefits
    unique_benefit_orgs = set([Benefit.objects.get(id=benefit).organisation for benefit in post_data.getlist("benefit")])
    
    if len(unique_benefit_orgs) == 0:
        return benefits_index(request, error="You must select at least one benefit")
    
    print (unique_benefit_orgs)
    if len(unique_benefit_orgs) > 1:
        return benefits_index(request, error="You can only assign benefits to opportunities that are owned by the same organisation")
    
    
    
    if request.method == "POST":
        context = {
            "hx": check_if_hx(request),
            "opportunities": Opportunity.objects.filter(organisation=organisation),
            "benefits": post_data.getlist("benefit")
        }
        return render(request, "org_admin/partials/assign_benefits.html", context=context)

def add_benefit_to_opportunity(request):
    if request.method == "POST":
        post_data = request.POST
        opprtunity_ids = post_data.getlist("opportunity_ids")
        benefits = post_data.getlist("benefit_ids")
        
        print(opprtunity_ids, benefits)
        
        for opp_id in opprtunity_ids:
            if check_ownership(request, Opportunity.objects.get(id=opp_id)):
                for benefit_id in benefits:
                    benefit = Benefit.objects.get(id=benefit_id)
                    if check_ownership(request, benefit):
                        OpportunityBenefit.objects.create(
                            opportunity=Opportunity.objects.get(id=opp_id),
                            benefit=benefit
                        )
        
        
        return benefits_index(request, success="Benefits have been assigned to the selected opportunities")
            
        
        return HTTPResponseHXRedirect("/org_admin/benefits/")


def unlink_benefit(request, link_id, opportunity_id):
    opp_benefit = OpportunityBenefit.objects.get(id=link_id)
    
    if check_ownership(request, opp_benefit.opportunity) and check_ownership(request, opp_benefit.benefit):
        opp_benefit.delete()
        return opportunity_details(request, opportunity_id, tab_name="benefits", success="Benefit has been unlinked from the opportunity")
    
    

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