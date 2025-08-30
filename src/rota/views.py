from django.shortcuts import render

from commonui.views import check_if_hx
from opportunities.models import Registration
from org_admin.models import OrganisationAdmin
from rota.models import Occurrence, VolunteerShift, Supervisor
from datetime import datetime
from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
from django.shortcuts import render
from commonui.views import check_if_hx
from django.contrib.auth import logout
from django.contrib.auth.views import PasswordResetView
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy


def get_supervisor_shifts(request):
    if not request.user.is_authenticated:
        return sign_in(request)

    if request.method == 'POST':
        return sign_in()

    user = request.user
    supervisors = Supervisor.objects.filter(user=user)
    admin = OrganisationAdmin.objects.filter(user=user)

    if not supervisors.exists() or not admin.exists():
        context = {
            "error" : "You do not have any supervisor account access"
        }
        return render(request, 'rota/sign_in.html', context)

    if request.user.is_superuser:
        occurrence = Occurrence.objects.filter(
            date__gte=datetime.now().date(),
        )

        shifts = []

        for shift in occurrence:
            shifts.append(
                {
                    'occurrence': shift,
                    'rsvp_yes': VolunteerShift.objects.filter(occurrence=shift, rsvp_response='yes', confirmed=True),
                    'rsvp_no': VolunteerShift.objects.filter(occurrence=shift, rsvp_response='no', confirmed=True),
                    'rsvp_null': VolunteerShift.objects.filter(occurrence=shift, rsvp_response='-', confirmed=True),
                    'opportunity': shift.one_off_date.opportunity
                },
            )

            print(shifts[-1]["rsvp_null"])

        context = {
            'shifts': shifts
        }

        return render(request, 'rota/shift_list.html', context)

    if admin.exists():
        occurrence = Occurrence.objects.filter(
            date__gte=datetime.now().date(),
            one_off_date__opportunity__organisation=admin.first().organisation
        )

        shifts = []

        for shift in occurrence:
            shifts.append(
                {
                    'occurrence': shift,
                    'rsvp_yes': VolunteerShift.objects.filter(occurrence=shift, rsvp_response='yes', confirmed=True),
                    'rsvp_no': VolunteerShift.objects.filter(occurrence=shift, rsvp_response='no', confirmed=True),
                    'rsvp_null': VolunteerShift.objects.filter(occurrence=shift, rsvp_response='-', confirmed=True),
                    'opportunity': shift.one_off_date.opportunity
                },
            )

        context = {
            'shifts' : shifts
        }

        return render(request, 'rota/shift_list.html', context)

    elif supervisors.exists():
        print('standard sup')
        #filter occurrences based on roles assigned to the supervisor
        shifts = []
        for supervisor in supervisors:
            print(supervisor)
            occurrences = None
            match supervisor.access_level:
                case 'all_org':
                    # All Occurrences for supervisor's organisation
                    org = supervisor.organisation
                    occurrences = Occurrence.objects.filter(
                        date__gte=datetime.now().date(),
                        one_off_date__opportunity__organisation=org
                    )

                case 'all_opportunity':
                    # All Occurrences for Opportunities linked to supervisor
                    supervisor_opps = supervisor.supervisor_opportunities.all()
                    occurrences = Occurrence.objects.filter(
                        date__gte=datetime.now().date(),
                        one_off_date__opportunity__in=supervisor_opps
                    )

                case 'all_role':
                    # All Occurrences for Roles linked to supervisor
                    supervisor_roles = supervisor.supervisor_roles.all()
                    occurrences = Occurrence.objects.filter(
                        date__gte=datetime.now().date(),
                        one_off_date__role__in=supervisor_roles
                    )

                case 'specific_shifts':
                    # Only assigned Occurrences
                    occurrences = supervisor.supervisor_shifts.filter(
                        date__gte=datetime.now().date()
                    )

                    print(occurrences)

            # Build shift context list for supervisor for filtered occurrences
            print('len', len(occurrences))
            for shift in occurrences:
                shifts.append(
                    {
                        'occurrence': shift,
                        'rsvp_yes': VolunteerShift.objects.filter(occurrence=shift, rsvp_response='yes', confirmed=True),
                        'rsvp_no': VolunteerShift.objects.filter(occurrence=shift, rsvp_response='no', confirmed=True),
                        'rsvp_null': VolunteerShift.objects.filter(occurrence=shift, rsvp_response='-', confirmed=True),
                        'opportunity': shift.one_off_date.opportunity
                    }
                )

        context = {
            'shifts':shifts
        }

        return render(request, 'rota/shift_list.html', context)

    print('uh oh')


# Create your views here.
def shift_supervisor(request, occurrence_id):
    occurrence = Occurrence.objects.get(id=occurrence_id)
    shifts = VolunteerShift.objects.filter(
        occurrence = occurrence,
        confirmed=True
    )

    for shift in shifts:
        if shift.status() == "stopped":
            shift.rsvp_response = 'no'
            shift.rsvp_reason = 'Automated: Volunteer stopped volunteering'
            shift.save()

    context = {
        'hx' : check_if_hx(request),
        'shifts' : shifts,
        'occurrence' : occurrence
    }

    return render(request, 'rota/role_screen.html', context)

def checkin_shift(request, shift_id):
    shift = VolunteerShift.objects.get(id=shift_id)
    if not shift.check_in_time:
        shift.check_in_time = datetime.now().time()
        shift.save()
    elif not shift.check_out_time:
        shift.check_out_time = datetime.now().time()
        shift.save()

    return shift_supervisor(request, shift.occurrence.id)

def sign_in(request):
    if request.method == "GET":
        return render(request, "rota/sign_in.html", {"hx": check_if_hx(request)})

    if request.method == "POST":
        username = request.POST["email"].lower()
        password = request.POST["password"]

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            request.method = "GET"
            return HttpResponseRedirect("/supervisor/")

        else:
            try:
                # get username from submitted email
                if username != "" or username != None:
                    user = User.objects.get(email=username)
                    username = user.username
                    user = authenticate(request, username=username, password=password)
                    if user is not None:
                        login(request, user)
                        return HttpResponseRedirect("/supervisor/")
                    else:
                        return render(request, "rota/sign_in.html",
                                      {"hx": check_if_hx(request), "error": "Incorrect username or password"})
                if user is not None:
                    login(request, user)
                    return HttpResponseRedirect("/supervisor/")
                else:
                    return render(request, "rota/sign_in.html",
                                  {"hx": check_if_hx(request), "error": "Incorrect username or password"})
            except Exception as e:
                return render(request, "rota/sign_in.html", {"hx": check_if_hx(request), "error": e})

def sign_out(request):
    if request.user.is_authenticated:
        logout(request)

    print('l_out')

    return get_supervisor_shifts(request)


class ResetPasswordView(SuccessMessageMixin, PasswordResetView):
    template_name = "rota/password_reset.html"
    email_template_name = "rota/password_reset_email.html"
    subject_template_name = "rota/password_reset_subject.txt"
    success_message = (
        "We've emailed you instructions for setting your password, "
        "if an account exists with the email you entered. You should receive them shortly."
        " If you don't receive an email, "
        "please make sure you've entered the address you registered with, and check your spam folder."
    )
    success_url = reverse_lazy("password_reset_sent_supervisor")

    # add hx context to the view
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["hx"] = check_if_hx(self.request)
        return context


def password_reset_sent(request):
    return render(
        request, "rota/password_reset_sent.html", {"hx": check_if_hx(request)}
    )