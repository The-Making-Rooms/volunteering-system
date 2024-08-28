from volunteer.models import SupplementaryInfo
from django.shortcuts import render
from django.http import HttpResponseRedirect
from commonui.views import check_if_hx
from .common import check_ownership
from organisations.models import Organisation, OrganisationAdmin

def additional_information(request, error=None, success=None):
    if not request.user.is_superuser:
        return HttpResponseRedirect("/volunteer")
    
    if request.user.is_superuser:
        additional_information = SupplementaryInfo.objects.all()
    else:
        additional_information = SupplementaryInfo.objects.filter(organisation=OrganisationAdmin.objects.get(user=request.user).organisation)
    
    
    
    if request.method == "GET":
        context = {
            "error": error,
            "success": success,
            "additional_information": additional_information,
            "hx": check_if_hx(request)
        }
        
        return render(request, "org_admin/manage_additional_information.html", context=context)

def delete_additional_info(request, id):
    if not request.user.is_superuser:
        return HttpResponseRedirect("/volunteer")
    
    try:
        additional_info = SupplementaryInfo.objects.get(id=id)
        additional_info.delete()
        return additional_information(request, success="Additional information deleted")
    except SupplementaryInfo.DoesNotExist:
        return additional_information(request, error="Additional information does not exist")
    
def add_additional_info(request):
    if not request.user.is_superuser:
        return HttpResponseRedirect("/org_admin")
    
    if request.method == "POST":
        data = request.POST
        
        title = data.get("title")
        description = data.get("description")
        
        if title == "" or description == "":
            return additional_information(request, error="Please fill in all fields")
        
        
        SupplementaryInfo.objects.create(
            title=title,
            description=description,
            organisation=OrganisationAdmin.objects.get(user=request.user).organisation if not request.user.is_superuser else None
        )
        
        request.method = "GET"
        return additional_information(request, success="Additional information added")
    else:
        context = {
            "hx": check_if_hx(request)
        }
        
        return render(request, "org_admin/additional_information.html", context=context)
    
def edit_additional_info(request, id):
    if not request.user.is_superuser:
        return HttpResponseRedirect("/org_admin")
    
    try:
        additional_info = SupplementaryInfo.objects.get(id=id)
        
        if not check_ownership(request, additional_info):
            request.method = "GET"
            return additional_information(request, error="You do not have permission to edit this additional information")
            
    except SupplementaryInfo.DoesNotExist:
        return additional_information(request, error="Additional information does not exist")
    
    if request.method == "GET":
        context = {
            "additional_info": additional_info,
            "hx": check_if_hx(request),
            "edit": True
        }
        
        return render(request, "org_admin/additional_information.html", context=context)
    
    if request.method == "POST":
        
        data = request.POST
        
        title = data.get("title")
        description = data.get("description")
        
        if title == "" or description == "":
            return additional_information(request, error="Please fill in all fields")
        
        additional_info.title = title
        additional_info.description = description
        additional_info.save()
        
        request.method = "GET"
        return additional_information(request, success="Additional information updated")