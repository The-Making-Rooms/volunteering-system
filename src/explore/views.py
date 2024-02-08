from django.shortcuts import render
from organisations.models import thematicCategory, organisationnThematicLink
from opportunities.models import Opportunity, Location, Image, Video, LinkedTags, Tag
from commonui.views import check_if_hx
# Create your views here.

def index(request):
    context = {
        "hx" : check_if_hx(request)
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
    results = Opportunity.objects.all()
    if theme:
        results = results.filter(organisation__thematic_category__name=theme)
    if stringsearch == '':
        pass
    if stringsearch:    
        results = results.filter(name__icontains=stringsearch)
    if organisation:
        results = results.filter(organisation__name__icontains=organisation)
    if tag:
        results = results.filter(linkedtags__tag__tag__icontains=tag)

    images = Image.objects.filter(opportunity__in=results)
    

    result_objs = []
    for result in results:
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
        "hx" : check_if_hx(request)
    }

    return render(request, 'explore/search.html', context=context)