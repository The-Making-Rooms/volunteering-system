from django.shortcuts import render
from commonui.views import check_if_hx
from .common import check_ownership
from ..models import OrganisationAdmin
from opportunities.models import Opportunity, Location, Image, Video, OpportunityView, Registration, RegistrationStatus, VolunteerRegistrationStatus
from .views import opportunity_admin

def opportunity_registrations(request, id=None, error=None, success=None):
    print ("got ID:", id, id == "all")
    if (id != None):

        if id == "all":
            opportunity = None
        else:  
            opportunity = Opportunity.objects.get(id=id)
            if not check_ownership(request, opportunity):
                return opportunity_admin(request, error="You do not have permission to view this opportunity")
        
    else:
        opportunity = None
    
    if request.user.is_superuser:
        opportunities = Opportunity.objects.all()
    else:
        opportunities = Opportunity.objects.filter(organisation=OrganisationAdmin.objects.get(user=request.user).organisation)
    
    registration_types = RegistrationStatus.objects.all()
    
    
    context = {
        "hx": check_if_hx(request),
        "opportunity": opportunity,
        "opportunities": opportunities,
        "registration_types": registration_types,
        "error": error,
        "success": success
    }
    
    return render(request, "org_admin/opportunity_registrations.html", context)

def set_selected_registration_status(request):
    if request.method == "POST":
        data = request.POST
        errors = []
        successes = []
        return_id = data.get('filter-by-opportunity') if "filter-by-opportunity" in data.keys() else None
        print(data.keys())
        selected_status_id = data["set-selected-status"]
        
        if selected_status_id == "":
            return opportunity_registrations(request, request.POST['filter-by-opportunity'], error="No status selected")
        
        if "registration_ids" in data.keys():
            registration_ids = data.getlist("registration_ids")
            #print(registration_ids)
            
            for registration_id in registration_ids:
                registration = Registration.objects.get(id=registration_id)
                
                
                if not request.user.is_superuser and registration.opportunity.organisation != OrganisationAdmin.objects.get(user=request.user).organisation:
                    return opportunity_registrations(request, return_id, error="You do not have permission to change the status of this registration")
                
                status = RegistrationStatus.objects.get(id=selected_status_id)
                
                if registration.get_registration_status() == status.status:
                    errors.append(f"{registration.volunteer.user.first_name} is already {status.status}")
                    continue
                
                if registration.get_registration_status() == "stopped" or registration.get_registration_status() == "completed":
                    errors.append(f"{registration.volunteer.user.first_name} needs to register again")
                    continue
                
                volunteer_registration_status = VolunteerRegistrationStatus(registration=registration, registration_status=status)
                volunteer_registration_status.save()
            
            if errors:
                return opportunity_registrations(request, return_id, error=errors)
            else:
                return opportunity_registrations(request, return_id, success="Statuses updated", error=errors)
            
        else:
            return opportunity_registrations(request, return_id, error="No registrations selected")

    else:
        return opportunity_admin(request, error="Invalid request")
    


def get_registration_table(request):
    print (request.POST)
    data = request.POST
    opportunity = data.get("filter-by-opportunity")
    name = data.get("filter-by-name")
    status = data.get("filter-by-status")
    
    print(opportunity, name, status)
    
    #aggregate 3 filters
    registrations = None
    
    if opportunity != "all":
        opportunity = Opportunity.objects.get(id=opportunity)
        registrations = Registration.objects.filter(opportunity=opportunity)
    else:
        if request.user.is_superuser:
            registrations = Registration.objects.all()
        else:
            registrations = Registration.objects.filter(opportunity__organisation=OrganisationAdmin.objects.get(user=request.user).organisation)
        
    if name != "":
        registrations = registrations.filter(volunteer__user__first_name__contains=name) | registrations.filter(volunteer__user__last_name__contains=name)
    
    if status != "all":
        status = RegistrationStatus.objects.get(id=status)
        registrations = [registration for registration in registrations if registration.get_registration_status() == status.status]
    
    context = {
        "registrations": registrations
    }
    
    return render(request, "org_admin/partials/registration_table.html", context)