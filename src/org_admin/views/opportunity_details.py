from django.shortcuts import render
from commonui.views import check_if_hx
from .common import check_ownership, check_schedule_dates
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
            
        lorem_ipsum = """
        Lorem ipsum odor amet, consectetuer adipiscing elit. Habitasse suspendisse semper ipsum netus nostra ac class enim. Rhoncus consequat neque natoque eget ornare id penatibus molestie orci. Adipiscing curabitur sed augue orci tortor in aliquam. Turpis vehicula taciti velit ligula diam inceptos litora penatibus. Ridiculus parturient libero eros velit orci leo nascetur sociosqu. Litora ante metus nec sed, vel elit mattis massa. Vehicula vehicula aliquam finibus et lacus; purus varius elit ornare. 
        """
            
        new_opportunity = Opportunity.objects.create(
            organisation=organisation,
            name="New Opportunity",
            description=lorem_ipsum,
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
        opp.save()
        
        opp.description = form_data["description"]
        opp.save()

        try: opp.featured = True if form_data["featured"] == "on" else False
        except KeyError: opp.featured = False

        try: opp.show_times_on_sign_up = True if form_data["show_times"] == "on" else False
        except KeyError: opp.show_times_on_sign_up = False

        try: opp.week_start = int(form_data["rota_day"]) if form_data["rota_day"] else 0
        except: opp.week_start = 0
        
        print(form_data)
        
        try:
            if form_data["active"] == "on":
                if not check_schedule_dates(opp):
                    request.method = "GET"
                    return opportunity_details(request, id, error="Opportunity must have a schedule to be active", index=True)
                opp.active = True
                opp.save()
            else:
                opp.active = False
                opp.save()
                
        except KeyError:
            opp.active = False
            opp.save()
            
        #try: opp.active = True if form_data["active"] == "on" else False
        #except: opp.active = False
        
        
        request.method = "GET"
        return opportunity_details(request, id, success="Opportunity updated successfully", index=True)
       
    

