from django.http import HttpResponse
from django.shortcuts import render
from django.template import loader
from organisations.models import Organisation, Link, Image, Video, Location
from opportunities.models import Opportunity, Image as OpportunityImage
from commonui.views import check_if_hx
from googlemaps import Client as GoogleMaps



# Create your views here.


def detail(request, organisation_id):
    template = loader.get_template("organisations/organisation_details.html")

    org = Organisation.objects.get(id=organisation_id)

    location = Location.objects.filter(organisation=org)

    print('CHEEESE')

    for site in location:
        print(site.longitude, site.latitude)
        if site.longitude is None or site.latitude is None:
            print('NO LONGITUDE OR LATITUDE')
            gmaps = GoogleMaps('AIzaSyA9FVyxMQjaCwmN_uHnvhXeSVGbwsTeMUY')
            geocode_result = gmaps.geocode(site.first_line + " " + site.postcode)
            site.longitude = geocode_result[0]['geometry']['location']['lng']
            site.latitude = geocode_result[0]['geometry']['location']['lat']
            site.save()


    links = Link.objects.filter(organisation=org)
    images = Image.objects.filter(organisation=org)
    videos = Video.objects.filter(organisation=org)


    context = {
        "organisation": org,
        "links": links,
        "images": images,
        "videos": videos,
        "locations": location,
        "hx": check_if_hx(request)
    }
    return HttpResponse(template.render(context, request))