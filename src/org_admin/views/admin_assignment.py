from org_admin.models import OrganisationAdmin
from organisations.models import Organisation
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from commonui.views import check_if_hx
from django.contrib.auth.forms import PasswordResetForm
from django.core.mail import send_mail
from django.conf import settings
import random


def get_admins(request, error=None, success=None):
    
    if not request.user.is_authenticated:
        return redirect("sign_in")
    elif not request.user.is_superuser and not OrganisationAdmin.objects.filter(user=request.user).exists():
        print("User is not an admin")
        return render(request, "org_admin/no_admin.html")
    
    
    if request.method == "GET":
        if request.user.is_superuser:
            admins = OrganisationAdmin.objects.all()
            organisations = Organisation.objects.all()
            superusers = User.objects.filter(is_superuser=True)
        else:
            organisation = OrganisationAdmin.objects.get(user=request.user).organisation
            admins = OrganisationAdmin.objects.filter(organisation=organisation)
            organisations = None
            superusers = None
            
        context = {
            "admins": admins,
            "error": error,
            "success": success,
            "superuser": request.user.is_superuser,
            "organisations": organisations,
            "superusers": superusers,
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
        
        
        email = data.get("email").lower()
            
        try:
            user = User.objects.get(email=email)
            org_admin_exists = OrganisationAdmin.objects.filter(user=user).exists()
            
            if not org_admin_exists:
                OrganisationAdmin.objects.create(user=user, organisation=org)
                request.method = "GET"
                
                send_mail(
                    subject='Welcome to Chip In',
                    message='You have been added as an admin to the organisation {}. Use the following link to login: http://chipinbwd.co.uk/org_admin/'.format(org.name),
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[email],
                    fail_silently=True,
                )
                
                return get_admins(request, success="Admin added")
            else:
                request.method = "GET"
                return get_admins(request, error="Admin already exists")
        except User.DoesNotExist:
            
            new_user = User.objects.create_user(email=email, username=email, password="".join(random.choices("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890", k=12)))
            new_user.save()
            org_admin = OrganisationAdmin.objects.create(user=new_user, organisation=org)
            
            
            prompt_mail = send_mail(
                subject='Welcome to Chip In',
                message="""You have been added as an admin to the organisation {}. Please visit the following link to reset your password: http://chipinbwd.co.uk/org_admin/password_reset/""".format(org.name),
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[email],
                fail_silently=True,
            )
            
            request.method = "GET"
            return get_admins(request, success="User was cretaed. Reset password to login")
            
                
                
def delete_admin(request, admin_id):
    
    if not request.user.is_authenticated:
        return redirect("sign_in")
    elif not request.user.is_superuser and not OrganisationAdmin.objects.filter(user=request.user).exists():
        return render(request, "org_admin/no_admin.html")

    
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
    

def add_super_user(request):
    
    if not request.user.is_authenticated:
        return redirect("sign_in")
    elif not request.user.is_superuser:
        return render(request, "org_admin/no_admin.html")
    
    if request.method == "POST":
        if request.user.is_superuser:
            data = request.POST
            email = data.get("email").lower()
            try:
                user = User.objects.get(email=email)
                user.is_superuser = True
                user.save()
                request.method = "GET"
                return get_admins(request, success="Superuser added")
            except User.DoesNotExist:
                request.method = "GET"
                return get_admins(request, error="User does not exist")
        else:
            request.method = "GET"
            return get_admins(request, error="You do not have permission to add a superuser")
        
    