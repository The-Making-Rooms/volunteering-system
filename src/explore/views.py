from django.shortcuts import render
from organisations.models import thematicCategory, organisationnThematicLink, Organisation
from organisations.models import Image as OrgImage
from opportunities.models import Opportunity, Location, Image, Video, LinkedTags, Tag
from commonui.views import check_if_hx
import random
from django.http import HttpResponseRedirect
from org_admin.models import OrganisationAdmin
# Create your views here.

def index(request):

    if request.user.is_authenticated:
        if request.user.is_superuser:
            print("user is superuser")
            return HttpResponseRedirect("/org_admin")
        elif OrganisationAdmin.objects.filter(user=request.user).exists():
            return HttpResponseRedirect("/org_admin")

    orgs = Organisation.objects.all()
    opps = Opportunity.objects.filter(active=True)
    org_objects = []

    opp_objects = []
    for opp in opps:
        opp_object = {
            "id": opp.id,
            "name": opp.name,
            "organisation": opp.organisation,
            "images": Image.objects.filter(opportunity=opp) if len(Image.objects.filter(opportunity=opp)) > 0 else OrgImage.objects.filter(organisation=opp.organisation),
        }
        try:
            print (opp_object['images'][0].image.url)
        except:
            pass
        opp_objects.append(opp_object)

    
    for org in orgs:
        org_object = {
            "id": org.id,
            "name": org.name,
            "description": org.description,
            "logo": org.logo,
            "images": OrgImage.objects.filter(organisation=org),
        }
        try:
            print (org_object['images'][0].image.url)
        except:
            pass
        org_objects.append(org_object)
        
    #randomise order of organisations
    random.shuffle(org_objects)
    
    #randomise order of opportunities
    random.shuffle(opp_objects)

    context = {
        "search" : True,
        "hx" : check_if_hx(request),
        "organisations": org_objects,
        "opportunities":  opp_objects,
        "link_active": "explore",
    }
    return render(request, 'explore/index.html', context=context)

def getTagResult(request, tag):
        try:
            tag = Tag.objects.get(tag=tag)
            linked_opps = LinkedTags.objects.filter(tag=tag)
            opps = Opportunity.objects.filter(id__in=linked_opps.values_list('opportunity', flat=True), active=True)
        except:
            opps = []
        try:
            #capitalise first letter of tag
            tag = tag[0].upper() + tag[1:]
            theme = thematicCategory.objects.get(name=tag)
            orgs = Organisation.objects.filter(id__in=organisationnThematicLink.objects.filter(theme=theme).values_list('organisation', flat=True))
        except:
            orgs = []
    
        result_objs = []
        for result in opps:
            res_obj = {
            "type": "opportunity",
            "id": result.id,
            "name": result.name,
            "description": result.description,
            "organisation": result.organisation,
            "images": Image.objects.filter(opportunity=result),
            "tags": LinkedTags.objects.filter(opportunity=result)
             }
            result_objs.append(res_obj)
            
        
        for org in orgs:
            res_obj = {
            "type": "organisation",
            "id": org.id,
            "name": org.name,
            "description": org.description,
            "logo": org.logo,
            "images": OrgImage.objects.filter(organisation=org),
            "tags": organisationnThematicLink.objects.filter(organisation=org)
            }
            result_objs.append(res_obj)
            
        context = {
            "search" : True,
            "results" : result_objs,
            "hx" : check_if_hx(request),
        }
        return render(request, 'explore/search.html', context)

def search(request):

    #get url params
    #theme = request.GET.get('theme')
    #stringsearch = request.GET.get('name')
    #organisation = request.GET.get('organisation')
    #tag = request.GET.get('tag')
    
    #get POST params
    print('search params:', request.POST.get('name'))
    theme = request.POST.get('theme')
    stringsearch = request.POST.get('name')
    organisation = request.POST.get('organisation')
    tag = request.POST.get('tag')


    #run query matching params
    results_opp = Opportunity.objects.all()
    results_org = Organisation.objects.all()

    #use stringsearch to filter results based on name, description, organisation name

    if stringsearch:
        results_opp = results_opp.filter(name__icontains=stringsearch)
        results_org = results_org.filter(name__icontains=stringsearch)
        if len(results_opp) == 0:
            results_opp = Opportunity.objects.all()
            results_opp = results_opp.filter(description__icontains=stringsearch)
        if len(results_opp) == 0:
            results_opp = Opportunity.objects.all()
            results_opp = results_opp.filter(organisation__name__icontains=stringsearch)
        if len(results_org) == 0:
            results_org = Organisation.objects.all()
            results_org = results_org.filter(description__icontains=stringsearch)
        if len(results_org) == 0:
            results_org = Organisation.objects.all()
            results_org = results_org.filter(name__icontains=stringsearch)
        
    

    result_objs = []
    for result in results_opp:
        res_obj = {
            "type": "opportunity",
            "id": result.id,
            "name": result.name,
            "description": result.description,
            "organisation": result.organisation,
            "images": Image.objects.filter(opportunity=result) if len(Image.objects.filter(opportunity=result)) > 0 else OrgImage.objects.filter(organisation=result.organisation),
            "tags": LinkedTags.objects.filter(opportunity=result)
        }
        result_objs.append(res_obj)

    for result in results_org:
        res_obj = {
            "type": "organisation",
            "id": result.id,
            "name": result.name,
            "description": result.description,
            "logo": result.logo,
            "images": OrgImage.objects.filter(organisation=result),
            "tags": organisationnThematicLink.objects.filter(organisation=result)
        }
        result_objs.append(res_obj)
    
    context = {
        "search" : True,
        "results" : result_objs,

        "hx" : check_if_hx(request),
        
    }
    
    print('search results:', result_objs)

    return render(request, 'explore/search.html', context=context)