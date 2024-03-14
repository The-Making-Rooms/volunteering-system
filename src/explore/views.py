from django.shortcuts import render
from organisations.models import thematicCategory, organisationnThematicLink, Organisation
from organisations.models import Image as OrgImage
from opportunities.models import Opportunity, Location, Image, Video, LinkedTags, Tag
from commonui.views import check_if_hx
# Create your views here.

def index(request):


    orgs = Organisation.objects.all()
    opps = Opportunity.objects.all()
    org_objects = []

    opp_objects = []
    for opp in opps:
        opp_object = {
            "id": opp.id,
            "name": opp.name,
            "images": Image.objects.filter(opportunity=opp),
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
            "images": OrgImage.objects.filter(organisation=org),
        }
        try:
            print (org_object['images'][0].image.url)
        except:
            pass
        org_objects.append(org_object)

    context = {
        "search" : True,
        "hx" : check_if_hx(request),
        "organisations": org_objects,
        "opportunities":  opp_objects,
        "link_active": "explore",
    }
    return render(request, 'explore/index.html', context=context)

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

    if theme:
        results_opp = results_opp.filter(organisation__thematic_category__name=theme)
    if stringsearch == '':
        pass
    if stringsearch:    
        results_opp = results_opp.filter(name__icontains=stringsearch)
    if organisation:
        results_opp = results_opp.filter(organisation__name__icontains=organisation)
    if tag:
        results_opp = results_opp.filter(linkedtags__tag__tag__icontains=tag)

    images = Image.objects.filter(opportunity__in=results_opp)
    
    

    result_objs = []
    for result in results_opp:
        res_obj = {
            "id": result.id,
            "name": result.name,
            "description": result.description,
            "images": Image.objects.filter(opportunity=result),
            "tags": LinkedTags.objects.filter(opportunity=result)
        }
        result_objs.append(res_obj)
    
    context = {
        "search" : True,
        "results" : result_objs,
        "opp_images" : images,
        "hx" : check_if_hx(request),
        
    }

    return render(request, 'explore/search.html', context=context)