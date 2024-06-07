from org_admin.models import OrganisationAdmin
from organisations.models import Organisation
from django.shortcuts import render
from django.contrib.auth.models import User
from commonui.views import check_if_hx

def get_admins(request, error=None, success=None):
    if request.method == "GET":
        if request.user.is_superuser:
            admins = OrganisationAdmin.objects.all()
            organisations = Organisation.objects.all()
        else:
            organisation = OrganisationAdmin.objects.get(user=request.user).organisation
            admins = OrganisationAdmin.objects.filter(organisation=organisation)
            organisations = None
            
        context = {
            "admins": admins,
            "error": error,
            "success": success,
            "superuser": request.user.is_superuser,
            "organisations": organisations,
            "hx": check_if_hx(request)
        }
        
        return render(request, "org_admin/organisation_admins.html", context=context)
    
    if request.method == "POST":
        data = request.POST
        
        if request.user.is_superuser:
            org_id = data.get("organisation_id")
            if org_id == "":
                request.method = "GET"
                return get_admins(request, error="Please select an organisation")
            org = Organisation.objects.get(id=org_id)
        else:
            org = OrganisationAdmin.objects.get(user=request.user).organisation
        
        
        email = data.get("email")
            
        try:
            user = User.objects.get(email=email)
            org_admin_exists = OrganisationAdmin.objects.filter(user=user).exists()
            
            if not org_admin_exists:
                OrganisationAdmin.objects.create(user=user, organisation=org)
                request.method = "GET"
                return get_admins(request, success="Admin added")
            else:
                request.method = "GET"
                return get_admins(request, error="Admin already exists")
        except User.DoesNotExist:
            request.method = "GET"
            return get_admins(request, error="User does not exist")
            
                
                
def delete_admin(request, admin_id):
    
    admin = OrganisationAdmin.objects.get(id=admin_id)
    number_of_admins = OrganisationAdmin.objects.filter(organisation=admin.organisation).count()
    
    if number_of_admins == 1:
        return get_admins(request, error="Cannot delete the only admin of an organisation")

    if admin.user == request.user:
        return get_admins(request, error="Cannot delete yourself")
    
    if request.user.is_superuser or admin.organisation == OrganisationAdmin.objects.get(user=request.user).organisation:
        admin.delete()
        return get_admins(request, success="Admin deleted")
    else:
        return get_admins(request, error="You do not have permission to delete this admin")
    
    