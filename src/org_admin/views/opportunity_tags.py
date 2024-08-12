
from .common import check_ownership
from .opportunity_details import opportunity_details, opportunity_admin_list
from opportunities.models import Opportunity, Tag, LinkedTags
from django.shortcuts import render


def tag_details(request, opportunity_id):
    opportunity = Opportunity.objects.get(id=opportunity_id)
    if not check_ownership(request, opportunity):
        return opportunity_admin_list(request, error="You do not have permission to view this opportunity")
    linked_tags = LinkedTags.objects.filter(opportunity=opportunity)
    
    context = {
        "opportunity": opportunity,
        "tags": linked_tags,
        "tab_name": "tags",
        "linked_tags": linked_tags
    }
    
    return render(request, "org_admin/partials/opportunity_tags.html", context)


def add_tag(request, opportunity_id=None, linked_tag_id=None, delete=False):
    if request.method == "GET":
        if delete:
            LinkedTags.objects.get(id=linked_tag_id).delete()
            return opportunity_details(request, opportunity_id, tab_name="details")
        return opportunity_details(request, opportunity_id, tab_name="details")
    if request.method == "POST":
        opportunity = Opportunity.objects.get(id=opportunity_id)
        
        if not check_ownership(request, opportunity):
            return opportunity_admin_list(request, error="You do not have permission to view this opportunity")
        
        if request.POST.get("tag") == "":
            request.method = "GET"
            return opportunity_details(request, opportunity_id, error="Tag cannot be empty", tab_name="details")
        
        try:
            tag = Tag.objects.get(tag=request.POST.get("tag").lower())
        except Tag.DoesNotExist:
            tag = Tag.objects.create(tag=request.POST.get("tag").lower())
            
        print(tag)
        
        try:
            new_tag = LinkedTags.objects.create(opportunity=opportunity, tag=tag)
        except:
            request.method = "GET"
            return opportunity_details(request, opportunity_id, error="Tag already exists", tab_name="details")
        
        request.method = "GET"
        return opportunity_details(request, opportunity_id, tab_name="details")