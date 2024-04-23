from django.http import HttpResponse
from django.shortcuts import render
from django.template import loader
from organisations.models import Organisation, Link, Image, Video, Location
from opportunities.models import Opportunity, Image as OpportunityImage
from commonui.views import check_if_hx
from googlemaps import Client as GoogleMaps
from communications.models import Chat
from org_admin.models import OrgnaisationAdmin
from commonui.views import HTTPResponseHXRedirect



# Create your views here

def create_chat(request, organisation_id):
    user = request.user
    
    if not user.is_authenticated:
        return HTTPResponseHXRedirect('/volunteer')

    try:
        chat = Chat.objects.get(organisation_id=organisation_id, participants=user)
        return HTTPResponseHXRedirect('/communications/' + str(chat.id) + '/')
    except Chat.DoesNotExist:
        pass
    

    organisation = Organisation.objects.get(id=organisation_id)
    org_admin = OrgnaisationAdmin.objects.filter(organisation=organisation)
    users = []
    for admin in org_admin:
        users.append(admin.user)
    users.append(user)
    # participants = models.ManyToManyField(User, related_name='chats')
    chat = Chat(
        organisation = organisation,
    )
    chat.save()
    chat.participants.add(*users)
    
    return HTTPResponseHXRedirect('/communications/' + str(chat.id) + '/')

def detail(request, organisation_id):
    template = loader.get_template("organisations/organisation_details.html")

    org = Organisation.objects.get(id=organisation_id)
    opps = Opportunity.objects.filter(organisation=org)
    location = Location.objects.filter(organisation=org)

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

    for site in location:
        print(site.longitude, site.latitude)
        if site.longitude is None or site.latitude is None:
            print('NO LONGITUDE OR LATITUDE')
            gmaps = GoogleMaps('AIzaSyBE66q11LMi6uYnd7_-9W8HIKzMOniqw6U')
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
        "opportunities": opp_objects,
        "hx": check_if_hx(request)
    }
    return HttpResponse(template.render(context, request))