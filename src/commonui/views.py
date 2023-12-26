from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from organisations.models import Organisation, Link, Image, Video
from opportunities.models import Opportunity, Image as OpportunityImage


# Create your views here.
def index(request):
    template = loader.get_template("commonui/index.html")

    orgs = Organisation.objects.all()
    opps = Opportunity.objects.all()
    org_objects = []

    opp_objects = []
    for opp in opps:
        opp_object = {
            "id": opp.id,
            "name": opp.name,
            "images": OpportunityImage.objects.filter(opportunity=opp),
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
            "location": org.location,
            "images": Image.objects.filter(organisation=org),
        }
        try:
            print (org_object['images'][0].image.url)
        except:
            pass
        org_objects.append(org_object)
    

    context = {
        "organisations": org_objects,
        "opportunities":  opp_objects,
    }
    return HttpResponse(template.render(context, request))