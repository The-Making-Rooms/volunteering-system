from django.shortcuts import render
from commonui.views import check_if_hx
from .common import check_ownership
from ..models import OrganisationAdmin
from opportunities.models import Opportunity, Location, Image, Video, OpportunityView, Registration, Tag, LinkedTags, SupplimentaryInfoRequirement

from organisations.models import Organisation 
import recurrence
import datetime


def create_new_opportunity(request):
    if request.method == "GET":
        if request.user.is_superuser:
            return render(request, "org_admin/create_new_opportunity.html", context={"hx": check_if_hx(request), "organisations": Organisation.objects.all(), "superuser": True})
        else:
            return render(request, "org_admin/create_new_opportunity.html", context={"hx": check_if_hx(request),})
    elif request.method == "POST":
        if request.user.is_superuser:
            try:
                organisation = Organisation.objects.get(id=request.POST["organisation_id"])
            except Organisation.DoesNotExist:
                return render(request, "org_admin/create_new_opportunity.html", context={"hx": check_if_hx(request), "error": "Organisation does not exist", "superuser": True})
        else:
            organisation = OrganisationAdmin.objects.get(user=request.user).organisation
            
        new_opportunity = Opportunity.objects.create(
            organisation=organisation,
            name="New Opportunity",
            description="New Opportunity",
            active=False,
            recurrences=recurrence.Recurrence(),
            end_time=datetime.datetime.now(),
            start_time=datetime.datetime.now(),
        )
        return opportunity_details(request, new_opportunity.id, success="Opportunity created successfully", index=True)
        


def create_new_opportunity_old(request):
    if request.user.is_superuser:
        if request.method == "POST":
            try:
                print(request.POST["organisation_id"])
                organisation = Organisation.objects.get(id=request.POST["organisation_id"])
            except OrganisationAdmin.DoesNotExist:
                print("Organisation does not exist")
                return render(request, "org_admin/opportunity_choose_organisation.html", context={"hx": check_if_hx(request), "error": "Organisation does not exist"})
            
            
            new_opportunity = Opportunity.objects.create(
                organisation=organisation,
                name="New Opportunity",
                description="New Opportunity",
                active=False,
                recurrences=recurrence.Recurrence(),
                end_time=datetime.datetime.now(),
                start_time=datetime.datetime.now(),
            )
            request.method = "GET"
            return opportunity_details(request, new_opportunity.id, success="Opportunity created successfully", index=True)
        else:
            return render(request, "org_admin/opportunity_choose_organisation.html", context={"hx": check_if_hx(request), "organisations": Organisation.objects.all()})
    
    if not request.user.is_superuser:
        new_opportunity = Opportunity.objects.create(
            organisation=OrganisationAdmin.objects.get(user=request.user).organisation,
            name="New Opportunity",
            description="New Opportunity",
            active=False,
            recurrences=recurrence.Recurrence(),
            end_time=datetime.datetime.now(),
            start_time=datetime.datetime.now(),
        )
        return opportunity_details(request, new_opportunity.id, success="Opportunity created successfully", index=True)



def opportunity_admin_list(request, error=None, success=None):
    print(request.user.is_superuser)
    #check if superuser
    if request.user.is_superuser:
        print("Superuser")
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
        "error": error,
        "success": success,
    }
        
    return render(
        request,
        "org_admin/opportunity_admin.html",
        context=context,
    )
    


def opportunity_details(request, id, error=None, success=None, index=False, tab_name=None):
    
    
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
            "error": error,
            "success": success,
            
            "tab_name": tab_name,
            "superuser": request.user.is_superuser,
        }
        
        if tab_name or index:
            return render(request, "org_admin/opportunity_details_admin.html", context=context)
        
        return render(request, "org_admin/partials/opportunity_details.html", context=context)
    elif request.method == "POST":
        if not check_ownership(request, Opportunity.objects.get(id=id)):
            return opportunity_admin_list(request, error="You do not have permission to view this opportunity")

        try:
            opp = Opportunity.objects.get(id=id)
        except Opportunity.DoesNotExist:
            return opportunity_admin_list(request, error="Opportunity does not exist")
        
        form_data = request.POST
        #print(form_data)
        
        opp.name = form_data["name"]
        opp.description = form_data["description"]

        try: opp.featured = True if form_data["featured"] == "on" else False
        except KeyError: opp.featured = False
            
        try: opp.active = True if form_data["active"] == "on" else False
        except: opp.active = False
        
        opp.save()
        
        request.method = "GET"
        return opportunity_details(request, id, success="Opportunity updated successfully", index=True)
       
    

