from django.shortcuts import render
from .models import OrgnaisationAdmin
from commonui.views import check_if_hx
from .forms import OrganisationDetailsForm, OrganisationLocationForm, OrganisationImageForm, OrgnaisationVideoForm, OrgnaisationLinkForm
from django.forms import formset_factory

# Create your views here.
def index (request):
    return render(request, 'org_admin/index.html', {'hx' : check_if_hx(request)})

def details(request):
    try:
        orgnaisation = OrgnaisationAdmin.objects.get(user=request.user)
    except OrgnaisationAdmin.DoesNotExist:
        return render(request, 'org_admin/no_admin.html', {'hx' : check_if_hx(request)})

    #prepare forms for the admin to edit the organisation
    organisation_form = OrganisationDetailsForm(instance=orgnaisation.organisation)

    context = {
        'organisation_form': organisation_form,
        'hx' : check_if_hx(request)
    }

    return render(request, 'org_admin/organisation_details_admin.html', context)
