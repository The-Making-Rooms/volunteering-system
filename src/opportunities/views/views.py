"""
VolunteeringSystem

This project is distributed under the CC BY-NC-SA 4.0 license. See LICENSE for details.
"""

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from opportunities.models import Opportunity, Benefit, Image, Video, SupplimentaryInfoRequirement, Registration, Location, RegistrationStatus, VolunteerRegistrationStatus, OpportunityView, LinkedTags, Tag, generate_random_pastel_hex, generate_darker_gradient_hex, Icon, OpportunitySection, OpportunityBenefit
from volunteer.models import SupplementaryInfo, SupplementaryInfoGrantee, VolunteerSupplementaryInfo, Volunteer
from organisations.models import Location as OrgLocation, Image as OrgImage, Video as OrgVideo
from django.template import loader
from googlemaps import Client as GoogleMaps
from ..forms import SuppInfoForm
from datetime import datetime, date
from django.forms import formset_factory
from communications.models import Chat
from django.core.mail import send_mail
import threading
from threading import Thread

from commonui.views import check_if_hx, HTTPResponseHXRedirect

from django.http import HttpResponse
from organisations.models import OrganisationAdmin

from rota.models import Role

# Create your views here.
def detail(request, opportunity_id):
    
    if request.user.is_authenticated:
        if request.user.is_superuser:
            print("user is superuser")
            return HttpResponseRedirect("/org_admin")
        elif OrganisationAdmin.objects.filter(user=request.user).exists():
            return HttpResponseRedirect("/org_admin")
        
    
    
    #print(opportunity_id)
    template = loader.get_template("opportunities/opportunity-details.html")
    opportunity = Opportunity.objects.get(id=opportunity_id)
    
    if opportunity.active == False:
        return HttpResponse('This opportunity is no longer active')
    
    benefits = [benefit.benefit for benefit in OpportunityBenefit.objects.filter(opportunity=opportunity)]
    text_rules_inclusion = []
    location = Location.objects.filter(opportunity=opportunity)
    sections = OpportunitySection.objects.filter(opportunity=opportunity)
    roles = Role.objects.filter(opportunity=opportunity)
    
    #print(opportunity.recurrences.rrules)
    #print(opportunity.recurrences.rdates)
    
    #Supplimental Information Requirements
    supp_info_reqs = SupplimentaryInfoRequirement.objects.filter(opportunity=opportunity)

    view = OpportunityView(opportunity=opportunity)
    view.save()

    if location.count() == 0:
        location = OrgLocation.objects.filter(organisation=opportunity.organisation)
        
    filtered_location = []
        
    for site in location:
        print(site.longitude, site.latitude)
        if site.longitude is None or site.latitude is None:
            print('NO LONGITUDE OR LATITUDE')
            site.delete()
        
            
    

    opp_images = Image.objects.filter(opportunity=opportunity) if len(Image.objects.filter(opportunity=opportunity)) > 0 else OrgImage.objects.filter(organisation=opportunity.organisation)
    opp_videos = Video.objects.filter(opportunity=opportunity)
    
    tags = LinkedTags.objects.filter(opportunity=opportunity)
    
    
    if len(opp_images) == 0:
        opp_images = OrgImage.objects.filter(organisation=opportunity.organisation)

    for rule in opportunity.recurrences.rrules:
        text_rules_inclusion.append(rule.to_text())

    exists = False
    active = False
    current_user = request.user
    if current_user.is_authenticated:
        try:
            check_1 = Registration.objects.filter(volunteer=Volunteer.objects.get(user=request.user), opportunity=opportunity).exists()
            latest_registration = Registration.objects.filter(volunteer=Volunteer.objects.get(user=request.user), opportunity=opportunity).order_by('-date_created').first()
            if latest_registration:
                check_2 = VolunteerRegistrationStatus.objects.filter(registration=latest_registration).order_by('-date').first().registration_status.status == 'stopped'
            else:
                check_2 = False
            if check_1:
                if not check_2:
                    print(check_1, check_2)
                    active = True
        except Volunteer.DoesNotExist:
            active = False
    context = {
        "opportunity": opportunity,
        "benefits": benefits,
        "text_rules_inclusion": text_rules_inclusion,
        "locations": location,
        "opp_images": opp_images,
        "opp_videos": opp_videos,
        "hx" : check_if_hx(request),
        "exists": active,
        "linked_tags": tags,
        "supp_info_reqs": supp_info_reqs,
        "sections": sections,
        "roles":roles
    }

    return HttpResponse(template.render(context, request))


def register_old(request, opportunity_id):
    #The registration process is as follows:
    #1. Check if the user is logged in
    #2. Check if the user has a volunteer profile
    #Query the opportunity if it requires any Additional Information
    #Generat a form with the Additional Information
    #If the form is valid, create a registration object
    #Grant organisaton access to the Additional Information
    #Return a success message

    if request.user.is_authenticated:
        current_user = request.user
        #check opportunity supplementary Inforequirements
        opportunity = Opportunity.objects.get(id=opportunity_id)
        
        if opportunity.active == False:
            return HttpResponse('You cannot register for this opportunity as it is no longer active') 
        
        try:
            check_1 = Registration.objects.filter(volunteer=Volunteer.objects.get(user=request.user), opportunity=opportunity).exists()
            latest_registration = Registration.objects.filter(volunteer=Volunteer.objects.get(user=request.user), opportunity=opportunity).order_by('-date_created').first()
            if latest_registration:
                check_2 = VolunteerRegistrationStatus.objects.filter(registration=latest_registration).order_by('-date').first().registration_status.status == 'stopped'
            else:
                check_2 = False
            if check_1:
                if not check_2:
                    print(check_1, check_2)
                    return HttpResponse('You are already registered for this opportunity') 
        except Volunteer.DoesNotExist:
            return HTTPResponseHXRedirect('/volunteer')
        
        supp_info_reqs = SupplimentaryInfoRequirement.objects.filter(opportunity=opportunity)
        #add the initial data to the form, if the user has already submitted the information
        SuppInfoFormSet = formset_factory(SuppInfoForm, extra=0)
        initial_data = []
        for req in supp_info_reqs:
            try:
                vol_supp_info = VolunteerSupplementaryInfo.objects.get(volunteer=Volunteer.objects.get(user=current_user), info=req.info)
                if vol_supp_info:
                    initial_data.append({'info': vol_supp_info.info, 'data': vol_supp_info.data})
            except VolunteerSupplementaryInfo.DoesNotExist:
                initial_data.append({'info': req.info, 'value': ''})
        #crete a form for the Additional Information
        formset = SuppInfoFormSet(initial=initial_data)


        if request.method == 'POST':
            #check if user is already registered
            check_1 = Registration.objects.filter(volunteer=Volunteer.objects.get(user=request.user), opportunity=opportunity).exists()
            latest_registration = Registration.objects.filter(volunteer=Volunteer.objects.get(user=request.user), opportunity=opportunity).order_by('-date_created').first()
            if latest_registration:
                check_2 = VolunteerRegistrationStatus.objects.filter(registration=latest_registration).order_by('-date').first().registration_status.status == 'stopped'
            else:
                check_2 = False
            if check_1:
                if not check_2:
                    print(check_1, check_2)
                    return HttpResponse('You are already registered for this opportunity') 

            
            if supp_info_reqs.count() == 0:
                registration = Registration(
                    volunteer = Volunteer.objects.get(user=current_user),
                    opportunity = opportunity
                )
                registration.save()

                volunteer_registration_status = VolunteerRegistrationStatus(
                    registration_status = RegistrationStatus.objects.get(status='awaiting_approval'),
                    date = date.today(),
                    registration = registration,
                )
                volunteer_registration_status.save()

                SendEmailToOrgAdminsThread(request, opportunity_id).start()
                return HTTPResponseHXRedirect('/volunteer/your-opportunities/')

            formset = SuppInfoFormSet(request.POST)
            if formset.is_valid():
                for form in formset:
                    #check if the user has already submitted the information, if so update it
                    try:
                        vol_supp_info = VolunteerSupplementaryInfo.objects.get(volunteer=Volunteer.objects.get(user=current_user), info=form.cleaned_data['info'])
                        vol_supp_info.data = form.cleaned_data['data']
                        vol_supp_info.last_updated = date.today()
                        vol_supp_info.save()
                    except VolunteerSupplementaryInfo.DoesNotExist:
                        vol_supp_info = VolunteerSupplementaryInfo(
                            volunteer = Volunteer.objects.get(user=current_user),
                            info = form.cleaned_data['info'],
                            data = form.cleaned_data['data'],
                            last_updated = date.today()
                        )
                        vol_supp_info.save()
                    #check if the organisation has already been granted access to the information, if not grant it
                    try:
                        supp_info_grantee = SupplementaryInfoGrantee.objects.get(org=opportunity.organisation, info=vol_supp_info)
                    except SupplementaryInfoGrantee.DoesNotExist:
                        supp_info_grantee = SupplementaryInfoGrantee(
                            org = opportunity.organisation,
                            info = vol_supp_info,
                            volunteer = Volunteer.objects.get(user=current_user)
                        )
                        supp_info_grantee.save()

                #create the registration object
                registration = Registration(
                    volunteer = Volunteer.objects.get(user=current_user),
                    opportunity = opportunity
                )
                registration.save()

                #create the volunteer registration status object
                volunteer_registration_status = VolunteerRegistrationStatus(
                    registration_status = RegistrationStatus.objects.get(status='awaiting_approval'),
                    date = date.today(),
                    registration = registration,
                )
                print("Volunteer Registration Status: ", volunteer_registration_status)
                volunteer_registration_status.save()
                
                #send email to the org_admins of the organisation
                
                        

                SendEmailToOrgAdminsThread(request, opportunity_id).start()
                return HTTPResponseHXRedirect('/volunteer/your-opportunities/')
            else:
                return HttpResponse('Form is not valid')
        else:
            req_info_titles_descs = []
            for req in supp_info_reqs:
                req_info_titles_descs.append({'title': req.info.title, 'description': req.info.description})

            
            context = {
                "formset": formset,
                "reqs": req_info_titles_descs,
                "hx": check_if_hx(request)
            }
            return render(request, 'opportunities/register.html', context=context)
    else:
        return HttpResponseRedirect('/volunteer')


def send_email_to_org_admins(request, opportunity_id):
    opportunity = Opportunity.objects.get(id=opportunity_id)
    org_admins = OrganisationAdmin.objects.filter(organisation=opportunity.organisation)
    subject = 'Chip in System - New Volunteer Registration'
    message = """
Hello {0},

A new volunteer has registered for the opportunity: {1}.
Please login to the Chip In system to view the volunteer's information and approve or deny their registration.

Regards,
The Chip In Team
""".format(opportunity.organisation.name, opportunity.name)
    for admin in org_admins:
        send_mail(subject, message, '', [admin.user.email], fail_silently=True)
        


class SendEmailToOrgAdminsThread(Thread):
    def __init__(self, request, opportunity_id):
        Thread.__init__(self)
        self.request = request
        self.opportunity_id = opportunity_id

    def run(self):
        send_email_to_org_admins(self.request, self.opportunity_id)