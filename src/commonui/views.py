from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from organisations.models import Organisation, Link, Image, Video
from opportunities.models import Opportunity, Image as OpportunityImage
from django.contrib.auth import authenticate, login
from webpush import send_user_notification


#create uswer
from django.contrib.auth.models import User

class HTTPResponseHXRedirect(HttpResponseRedirect):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self["HX-Redirect"] = self["Location"]

    status_code = 200

def check_if_hx(request):
    try:
        hx_request = request.headers['HX-Request']
        return True
    except KeyError:
        return False

# Create your views here.
def index(request):
    template = loader.get_template("commonui/index.html")

    orgs = Organisation.objects.filter(featured=True)
    opps = Opportunity.objects.filter(featured=True)
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
        "hx": check_if_hx(request),
        "link_active": "index",
    }

    payload = {"head": "Welcome!", "body": "Hello World"}

    return HttpResponse(template.render(context, request))


def index_alias(request):
    return index()

def authenticate_user(request):
    username = request.POST["email"]
    password = request.POST["password"]

    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        return HTTPResponseHXRedirect(request.headers['HX-Current-URL'])

    else:
        return render(request, 'commonui/not_logged_in.html', {'hx':check_if_hx(request), 'login_failed': True})
    

def create_account(request):
    if request.method == "POST":

        print(request.POST)

        email = request.POST["email"]
        username = request.POST["username"]
        password = request.POST["password"]
        user = User.objects.create_user(username, email, password)
        user.save()
        user = authenticate(request, username=username, password=password)
        login(request, user)

        return HTTPResponseHXRedirect('/volunteer')
    else:
        return render(request, 'commonui/create_user_account.html', {'hx': check_if_hx(request)})