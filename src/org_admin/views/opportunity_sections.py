from django.shortcuts import render
from ..models import OrganisationAdmin
from opportunities.models import Opportunity, OpportunitySection
from .common import check_ownership
from .opportunity_details import opportunity_details, opportunity_admin_list

def opportunity_sections(request, id):
    opportunity = Opportunity.objects.get(id=id)
    sections = OpportunitySection.objects.filter(opportunity=opportunity)
    
    context = {
        "opportunity": opportunity,
        "sections": sections
    }
    
    return render(request, "org_admin/partials/opportunity_sections.html", context)

def move_section_up(request, section_id):
    section = OpportunitySection.objects.get(id=section_id)
    opportunity = section.opportunity
    if not check_ownership(request, opportunity):
        return opportunity_admin_list(request, error="You do not have permission to view this opportunity")
    else:
        sections = OpportunitySection.objects.filter(opportunity=opportunity)
        sections = list(sections)
        index = sections.index(section)
        if index > 0:
            temp = sections[index-1]
            sections[index-1] = section
            sections[index] = temp
            for i, section in enumerate(sections):
                section.order = i
                section.save()
        return opportunity_details(request, opportunity.id, tab_name="sections")
    
def move_section_down(request, section_id):
    section = OpportunitySection.objects.get(id=section_id)
    opportunity = section.opportunity
    if not check_ownership(request, opportunity):
        return opportunity_admin_list(request, error="You do not have permission to view this opportunity")
    else:
        sections = OpportunitySection.objects.filter(opportunity=opportunity)
        sections = list(sections)
        index = sections.index(section)
        if index < len(sections) - 1:
            temp = sections[index+1]
            sections[index+1] = section
            sections[index] = temp
            for i, section in enumerate(sections):
                section.order = i
                section.save()
        return opportunity_details(request, opportunity.id, tab_name="sections")
    
def delete_section(request, section_id):
    section = OpportunitySection.objects.get(id=section_id)
    opportunity = section.opportunity
    if not check_ownership(request, opportunity):
        return opportunity_admin_list(request, error="You do not have permission to view this opportunity")
    else:
        section.delete()
        return opportunity_details(request, opportunity.id, tab_name="sections")
    
    
def create_new_section(request, opportunity_id):
    if request.method == "POST":
        data = request.POST
        opportunity = Opportunity.objects.get(id=opportunity_id)
        if not check_ownership(request, opportunity):
            request.method = "GET"
            return opportunity_admin_list(request, error="You do not have permission to view this opportunity")
        
        section = OpportunitySection.objects.create(opportunity=opportunity, title=data['name'], content=data['description'], order=OpportunitySection.objects.filter(opportunity=opportunity).count()-1)
        section.save()
        request.method = "GET"
        return opportunity_details(request, opportunity.id, tab_name="sections", success="Section created successfully")
    else:
        opportunity = Opportunity.objects.get(id=opportunity_id)
        if not check_ownership(request, opportunity):
            return opportunity_admin_list(request, error="You do not have permission to view this opportunity")
        
        context = {
            "opportunity": opportunity,
        }
        
        return render(request, "org_admin/partials/opportunity_section_editor.html", context)

    
def edit_section(request, section_id):
    if request.method == "POST":
        data = request.POST
        section = OpportunitySection.objects.get(id=section_id)
        opportunity = section.opportunity
        if not check_ownership(request, opportunity):
            request.method = "GET"
            return opportunity_admin_list(request, error="You do not have permission to view this opportunity")
        
        section.title = data['name']
        section.content = data['description']
        section.save()
        request.method = "GET"
        return opportunity_details(request, opportunity.id, tab_name="sections", success="Section updated successfully")
    else:
        section = OpportunitySection.objects.get(id=section_id)
        opportunity = section.opportunity
        if not check_ownership(request, opportunity):
            return opportunity_admin_list(request, error="You do not have permission to view this opportunity")
        
        context = {
            "opportunity": opportunity,
            "section": section
        }
        
        return render(request, "org_admin/partials/opportunity_section_editor.html", context)