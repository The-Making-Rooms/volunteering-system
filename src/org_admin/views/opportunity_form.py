from commonui.views import check_if_hx
from django.shortcuts import render
from opportunities.models import Opportunity
from .common import check_ownership
from .opportunity_details import opportunity_admin_list, opportunity_details
from forms.models import Form

def opportunity_form(request, error=None, success=None, id=None):
    
    try:
        if id:
            opportunity = Opportunity.objects.get(id=id)
            if not check_ownership(request, opportunity):
                return opportunity_admin_list(request, error="You do not have permission to view this opportunity")
            
        else:
            return opportunity_admin_list(request, error="Opportunity ID not provided")
    except Opportunity.DoesNotExist:
        return opportunity_admin_list(request, error="Opportunity does not exist")
    except Exception as e:
        return opportunity_admin_list(request, error="An error occurred: " + str(e))
    
    
    if request.method == "POST":
        form_data = request.POST
        
        print ("Form data: ", form_data)
        
        if form_data.get("form") and (form_data.get("form") != ""):
            try:
                
                if form_data.get("form") == "none":
                    opportunity.form = None
                    opportunity.save()
                    request.method = "GET"
                    return opportunity_details(request, id, success="Form removed successfully", tab_name="form")
                
                form = Form.objects.get(id=form_data["form"])
                if not check_ownership(request, form):
                    return opportunity_details(request, id, error="You do not have permission to view this form", tab_name="form")
                opportunity.form = form
                opportunity.save()
                request.method = "GET"
                return opportunity_details(request, id, success="Form updated successfully", tab_name="form")
                
            except Form.DoesNotExist:
                return opportunity_details(request, id, error="Form does not exist", tab_name="form")
        else:
            return opportunity_details(request, id, error="Form ID not provided", tab_name="form")
        

    
    forms = Form.objects.filter(organisation=opportunity.organisation)
    
    context = {
    "hx": check_if_hx(request),
    "forms": forms,
    "error": error,
    "success": success,
    "tab_name": "form",
    "opportunity": opportunity,
    "superuser": request.user.is_superuser,
    }
    
    return render(request, "org_admin/partials/opportunity_form.html", context=context)