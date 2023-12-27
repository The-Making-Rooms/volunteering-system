from django.http import HttpResponse
from django.shortcuts import render
from django.template import loader
from organisations.models import Organisation, Link, Image, Video
from opportunities.models import Opportunity, Image as OpportunityImage
from commonui.views import check_if_hx
# Create your views here.


def detail(request, organisation_id):
    template = loader.get_template("organisations/organisation_details.html")

    org = Organisation.objects.get(id=organisation_id)

    links = Link.objects.filter(organisation=org)
    images = Image.objects.filter(organisation=org)
    videos = Video.objects.filter(organisation=org)


    context = {
        "organisation": org,
        "links": links,
        "images": images,
        "videos": videos,
        "hx": check_if_hx(request)
    }
    return HttpResponse(template.render(context, request))