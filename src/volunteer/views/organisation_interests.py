from organisations.models import Organisation, OrganisationInterest 
from django.shortcuts import render, redirect
from commonui.views import HTTPResponseHXRedirect
from django.http import HttpResponseRedirect

def toggle_interest(request, organisation_id):
    organisation = Organisation.objects.get(id=organisation_id)
    
    if request.user.is_authenticated:
        exists = OrganisationInterest.objects.filter(volunteer__user=request.user, organisation=organisation).exists()
        if not exists:
            OrganisationInterest.objects.create(volunteer=request.user.volunteer, organisation=organisation)
        else:
            OrganisationInterest.objects.filter(volunteer__user=request.user, organisation=organisation).delete()
            
    return HttpResponseRedirect('/volunteer/')


