from django.forms import ValidationError
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse_lazy
from organisations.models import Organisation, Link, Image, Video
from opportunities.models import Opportunity, Image as OpportunityImage
from django.contrib.auth import authenticate, login
from webpush import send_user_notification
from django.contrib.auth.views import PasswordResetView
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.password_validation import validate_password
import random
from org_admin.models import OrganisationAdmin

# create uswer
from django.contrib.auth.models import User


class HTTPResponseHXRedirect(HttpResponseRedirect):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self["HX-Redirect"] = self["Location"]
        print(self["HX-Redirect"])

    status_code = 200


def check_if_hx(request):
    try:
        hx_request = request.headers["HX-Request"]
        return True
    except KeyError:
        return False


class ResetPasswordView(SuccessMessageMixin, PasswordResetView):
    template_name = "commonui/password_reset.html"
    email_template_name = "commonui/password_reset_email.html"
    subject_template_name = "commonui/password_reset_subject.txt"
    success_message = (
        "We've emailed you instructions for setting your password, "
        "if an account exists with the email you entered. You should receive them shortly."
        " If you don't receive an email, "
        "please make sure you've entered the address you registered with, and check your spam folder."
    )
    success_url = reverse_lazy("password_reset_sent_user")

    # add hx context to the view
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["hx"] = check_if_hx(self.request)
        return context


def password_reset_sent(request):
    print("password reset sent")
    return render(
        request, "commonui/password_reset_sent.html", {"hx": check_if_hx(request)}
    )

def redirect_admins(request):
    if request.user.is_authenticated:
        print("user is authenticated")
        if request.user.is_superuser:
            print("user is superuser")
            return HttpResponseRedirect("/org_admin")
        if OrganisationAdmin.objects.filter(user=request.user).exists():
            return HttpResponseRedirect("/org_admin")
            

# Create your views here.
def index(request):
    
    if request.user.is_authenticated:
        if request.user.is_superuser:
            print("user is superuser")
            return HttpResponseRedirect("/org_admin")
        elif OrganisationAdmin.objects.filter(user=request.user).exists():
            return HttpResponseRedirect("/org_admin")
    
    template = loader.get_template("commonui/index.html")
    orgs = Organisation.objects.filter(featured=True)
    opps = Opportunity.objects.filter(featured=True)
    org_objects = []

    opp_objects = []
    for opp in opps:
        opp_object = {
            "id": opp.id,
            "name": opp.name,
            "description": opp.description,
            "organisation": opp.organisation,
            "images": OpportunityImage.objects.filter(opportunity=opp) if len(OpportunityImage.objects.filter(opportunity=opp)) > 0 else Image.objects.filter(organisation=opp.organisation),
        }
        try:
            print(opp_object["images"][0].image.url)
        except:
            pass
        opp_objects.append(opp_object)

    for org in orgs:
        org_object = {
            "id": org.id,
            "name": org.name,
            "logo": org.logo,
            "description": org.description,
            "images": Image.objects.filter(organisation=org),
        }
        try:
            print(org_object["images"][0].image.url)
        except:
            pass
        org_objects.append(org_object)
        
    #randomise order of organisations
    random.shuffle(org_objects)
    
    #randomise order of opportunities
    random.shuffle(opp_objects)
    

    context = {
        "organisations": org_objects,
        "opportunities": opp_objects,
        "hx": check_if_hx(request),
        "link_active": "index",
    }

    return HttpResponse(template.render(context, request))


def index_alias(request):
    return index()


def authenticate_user(request):
    username = request.POST["email"]
    password = request.POST["password"]

    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        return HTTPResponseHXRedirect(request.headers["HX-Current-URL"])

    else:
        try:
            #get username from submitted email
            if username != "" or username != None:
                user = User.objects.get(email=username)
                username = user.username
                user = authenticate(request, username=username, password=password)
                if user is not None:
                    login(request, user)
                    return HTTPResponseHXRedirect(request.headers["HX-Current-URL"])
            if user is not None:
                login(request, user)
                return HTTPResponseHXRedirect(request.headers["HX-Current-URL"])
        except:
            pass

        return render(
            request,
            "commonui/not_logged_in.html",
            {"hx": check_if_hx(request), "login_failed": True},
        )


def create_account(request):
    if request.method == "POST":

        data = request.POST

        if User.objects.filter(email=data["email"]).exists():
            return render(request, "commonui/error.html", {"hx": check_if_hx(request), "error": "Email already in use"})
        
        if data["password"] != data["password_confirm"]:
            return render(request, "commonui/error.html", {"hx": check_if_hx(request), "error": "Passwords do not match"})
        
        #check password is secure enough
        try:
            validate_password(data["password"])
        except ValidationError as e:
            return render(request, "commonui/error.html", {"hx": check_if_hx(request), "error": e})
        
        
        #print(data)
        username = "".join(random.choices("abcdefghijklmnopqrstuvwxyz", k=10))
        #ensure a user with that username does not exist
        while User.objects.filter(username=username).exists():
            username = "".join(random.choices("abcdefghijklmnopqrstuvwxyz", k=10))
        # create django user
        user = User.objects.create_user(username, data["email"], data["password"])
        user.save()
        user = authenticate(request, username=username, password=data["password"])
        login(request, user)

        return HTTPResponseHXRedirect("/volunteer")
    else:
        return render(
            request, "commonui/create_user_account.html", {"hx": check_if_hx(request)}
        )
