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


# create uswer
from django.contrib.auth.models import User


class HTTPResponseHXRedirect(HttpResponseRedirect):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self["HX-Redirect"] = self["Location"]

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
    success_url = reverse_lazy("password_reset_sent")

    # add hx context to the view
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["hx"] = check_if_hx(self.request)
        return context


def password_reset_sent(request):
    return render(
        request, "commonui/password_reset_sent.html", {"hx": check_if_hx(request)}
    )


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
            "description": opp.description,
            "organisation": opp.organisation,
            "images": OpportunityImage.objects.filter(opportunity=opp),
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

        print(request.POST)

        email = request.POST["email"]
        username = request.POST["username"]
        password = request.POST["password"]
        user = User.objects.create_user(username, email, password)
        user.save()
        user = authenticate(request, username=username, password=password)
        login(request, user)

        return HTTPResponseHXRedirect("/volunteer")
    else:
        return render(
            request, "commonui/create_user_account.html", {"hx": check_if_hx(request)}
        )
