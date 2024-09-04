from django.shortcuts import render
from ..models import OrganisationAdmin
from organisations.models import Organisation, OrganisationSection
from .common import check_ownership
from .views import details as org_details

def organisation_sections(request, id):
    organisation = Organisation.objects.get(id=id)
    sections = OrganisationSection.objects.filter(organisation=organisation)
    
    context = {
        "organisation": organisation,
        "sections": sections
    }
    
    return render(request, "org_admin/partials/opportunity_sections.html", context)

def org_move_section_up(request, section_id):
    section = OrganisationSection.objects.get(id=section_id)
    organisation = section.organisation
    admin = OrganisationAdmin.objects.filter(user=request.user, organisation=organisation).exists()
    if not admin and not request.user.is_superuser:
        return org_details(request, error="You do not have permission to view this organisation")
    else:
        sections = OrganisationSection.objects.filter(organisation=organisation)
        sections = list(sections)
        index = sections.index(section)
        if index > 0:
            temp = sections[index-1]
            sections[index-1] = section
            sections[index] = temp
            for i, section in enumerate(sections):
                section.order = i
                section.save()
        if not request.user.is_superuser:
            return org_details(request)
        else:
            return org_details(request, organisation_id=organisation.id)
    
def org_move_section_down(request, section_id):
    section = OrganisationSection.objects.get(id=section_id)
    organisation = section.organisation
    admin = OrganisationAdmin.objects.filter(user=request.user, organisation=organisation).exists()
    if not admin and not request.user.is_superuser:
        return org_details(request, error="You do not have permission to view this organisation")
    else:
        sections = OrganisationSection.objects.filter(organisation=organisation)
        sections = list(sections)
        index = sections.index(section)
        if index < len(sections) - 1:
            temp = sections[index+1]
            sections[index+1] = section
            sections[index] = temp
            for i, section in enumerate(sections):
                section.order = i
                section.save()
                
                
        if not request.user.is_superuser:
            return org_details(request)
        else:
            return org_details(request, organisation_id=organisation.id)
    
def org_delete_section(request, section_id):
    section = OrganisationSection.objects.get(id=section_id)
    organisation = section.organisation
    admin = OrganisationAdmin.objects.filter(user=request.user, organisation=organisation).exists()
    if not admin and not request.user.is_superuser:
        return org_details(request, error="You do not have permission to view this organisation")

    else:
        section.delete()
        
        
        if not request.user.is_superuser:
            return org_details(request)
        else:
            return org_details(request, organisation_id=organisation.id)
    
    
def org_create_new_section(request, organisation_id):
    if request.method == "POST":
        data = request.POST
        organisation = Organisation.objects.get(id=organisation_id)
        admin = OrganisationAdmin.objects.get(user=request.user)
        print(admin.organisation)
        if (admin.organisation != organisation) and not request.user.is_superuser:
            return org_details(request, error="You do not have permission to view this organisation")
        
        section = OrganisationSection.objects.create(organisation=organisation, title=data['name'], content=data['description'], order=OrganisationSection.objects.filter(organisation=organisation).count()-1)
        section.save()
        request.method = "GET"
        if not request.user.is_superuser:
            return org_details(request)
        else:
            return org_details(request, organisation_id=organisation.id)
    else:
        organisation = Organisation.objects.get(id=organisation_id)
        admin = OrganisationAdmin.objects.get(user=request.user)
        print(admin.organisation)
        print(organisation)
        if (admin.organisation != organisation) and not request.user.is_superuser:
            return org_details(request, error="You do not have permission to view this organisation")
        
        context = {
            "organisation": organisation
        }
        
        return render(request, "org_admin/partials/organisation_section_editor.html", context)

    
def org_edit_section(request, section_id):
    if request.method == "POST":
        data = request.POST
        section = OrganisationSection.objects.get(id=section_id)
        organisation = section.organisation
        admin = OrganisationAdmin.objects.filter(user=request.user, organisation=organisation).exists()
        if not admin and not request.user.is_superuser:
            return org_details(request, error="You do not have permission to view this organisation")
        
        section.title = data['name']
        section.content = data['description']
        section.save()
        request.method = "GET"
        if not request.user.is_superuser:
            return org_details(request)
        else:
            return org_details(request, organisation_id=organisation.id)
    else:
        section = OrganisationSection.objects.get(id=section_id)
        organisation = section.organisation
        admin = OrganisationAdmin.objects.filter(user=request.user, organisation=organisation).exists()
        if not admin and not request.user.is_superuser:
            return org_details(request, error="You do not have permission to view this organisation")
        
        context = {
            "organisation": organisation,
            "section": section
        }
        
        return render(request, "org_admin/partials/organisation_section_editor.html", context)