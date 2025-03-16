from django.forms import ValidationError
from org_admin.models import OrganisationAdmin
from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib.auth.password_validation import validate_password
from commonui.views import check_if_hx, HTTPResponseHXRedirect
from ..models import NotificationPreference



def profile(request):
    if request.method == "POST":
        user = request.user
        send_email_on_message, created = NotificationPreference.objects.get_or_create(user=request.user)
        send_email_on_message= send_email_on_message.email_on_message
        
        if request.POST.get("first_name") == "":
            return render(request, "org_admin/profile.html", {"error": "First name cannot be empty"})
        else:
            user.first_name = request.POST.get("first_name")
            user.save()
            
        if request.POST.get("last_name") == "":
            return render(request, "org_admin/profile.html", {"error": "Last name cannot be empty"})
        else: 
            user.last_name = request.POST.get("last_name")
            user.save()
            
        return render(request, "org_admin/profile.html", {"success": "Profile updated", "hx": check_if_hx(request), "send_email_on_message": send_email_on_message})
    else:
        send_email_on_message, created = NotificationPreference.objects.get_or_create(user=request.user)
        send_email_on_message= send_email_on_message.email_on_message
        user = request.user
        admin = OrganisationAdmin.objects.get(user=user)
        return render(request, "org_admin/profile.html", {"admin": admin, "user": user, "hx": check_if_hx(request), "send_email_on_message": send_email_on_message})

def toggle_message_on_email(request):
    prefs, created = NotificationPreference.objects.get_or_create(user=request.user)
    prefs.email_on_message = not prefs.email_on_message
    prefs.save()
    request.method = "GET"
    return profile(request)
    

def change_password(request):
    if request.method == "POST":
        user = request.user
        
        old_password = request.POST.get("old_password")
        
        password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")
        
        if not user.check_password(old_password):
            return render(request, "org_admin/profile.html", {"error": "Old password is incorrect", "hx": check_if_hx(request)})
        
        if password != confirm_password:
            return render(request, "org_admin/profile.html", {"error": "Passwords do not match" , "hx": check_if_hx(request)})
        
        try:
            validate_password(password)
        except ValidationError as e:
            return render(request, "org_admin/profile.html", {"error": e, "hx": check_if_hx(request)})
        
        user.set_password(password)
        
        user.save()
        
        return HTTPResponseHXRedirect('/org_admin/sign_in/')
    
def logout_view(request):
    logout(request)
    return HTTPResponseHXRedirect('/org_admin/sign_in/')