from django.shortcuts import render
from commonui.views import check_if_hx
import random
import string
from django.contrib.auth.models import User
from communications.models import Message, Chat
from organisations.models import OrganisationView, OrganisationInterest, OrganisationAdmin, Organisation
from opportunities.models import Registration, VolunteerRegistrationStatus, Opportunity, OpportunityView
from volunteer.models import MentorRecord, MentorSession, Volunteer
from forms.models import Form, Question, Response, Answer, Options
import datetime

"""
Types of data widgets:

Numeric - Format:
{
    "type": "numeric",
    "title": "Title",
    "value": 0,
}

pie chart - Format:
{
    "type": "pie",
    "title": "Title",
    "data": [
        {
            "label": "Label",
            "value": 0,
        },
    ]
}

bar chart - Format:
{
    "type": "bar",
    "title": "Title",
    "data": [
        {
            "label": "Label",
            "value": 0,
        },
    ]
}

List - Format:
{
    "type": "list",
    "title": "Title",
    "data": [
        {
            "label": "Label",
            "value": "Value",
            "href": "URL",
        },
    ]
}

"""

def dashboard_index(request):
    

    context = {
        "hx": check_if_hx(request),
        "sections": get_chipin_admin_data(request),
    }
    return render(
        request,
        "org_admin/dashboard.html",
        context=context,
    )
    
def get_mentor_data(request, organisation_id=None):
    if request.user.is_superuser and organisation_id:
        organisation = Organisation.objects.get(id=organisation_id)
    elif not request.user.is_superuser:
        organisation = OrganisationAdmin.objects.get(user=request.user).organisation
    else:
        organisation = None
    
    if organisation:
        mentees = MentorRecord.objects.filter(organisation=organisation)
    else:
        mentees = MentorRecord.objects.all()
    
    try:
        mentor_start_form = Form.objects.get(mentor_start_form=True)
        mentor_end_form = Form.objects.get(mentor_end_form=True)
    except Form.DoesNotExist:
        mentor_start_form = None
        mentor_end_form = None
    
    completed_start_form = 0
    completed_end_form = 0
    
    if mentor_start_form and mentor_end_form:
        for mentee in mentees:
            if Response.objects.filter(form=mentor_start_form, user=mentee.volunteer.user):
                completed_start_form += 1
            if Response.objects.filter(form=mentor_end_form, user=mentee.volunteer.user):
                completed_end_form += 1
                
        active_mentees = mentees.count() - completed_end_form
        
        mentor_data_sections.append({
            "type": "numeric",
            "title": "Active Mentees",
            "value": active_mentees,
        })
            
    mentor_data_sections = []
    

    
    mentor_data_sections.append({
        "type": "numeric",
        "title": "Total Mentees",
        "value": len(mentees),
    })
    
    mentor_data_sections.append({
        "type": "numeric",
        "title": "Completed Initial Questionnaire",
        "value": completed_start_form,
    })
    
    mentor_data_sections.append({
        "type": "numeric",
        "title": "Completed Exit Questionnaire",
        "value": completed_end_form,
    })
    
    for section in mentor_data_sections:
        section["id"] = ''.join(random.choices(string.ascii_uppercase, k=10))
        
    return mentor_data_sections
    
def get_volunteer_data(request, organisation_id=None):
    if request.user.is_superuser and organisation_id:
        organisation = Organisation.objects.get(id=organisation_id)
    elif not request.user.is_superuser:
        organisation = OrganisationAdmin.objects.get(user=request.user).organisation
    else:
        organisation = None
    
    
     #Volunteer data - Volunteer age brackets, gender make up, ethnicity make up
    volunteer_data_sections = []
    
    if organisation:
        volunteer_dobs = [reg.volunteer.date_of_birth for reg in Registration.objects.filter(opportunity__organisation=organisation)]
    else:
        volunteer_dobs = [volunteer.date_of_birth for volunteer in Volunteer.objects.all()]
    
    
    volunteer_ages = [datetime.datetime.now().year - dob.year for dob in volunteer_dobs]
    volunteer_ages.sort()
    #sor into age brackets of 13-18, 19-25, 26-35, 36-45, 46-55, 56-65, 66-75, 76-85, 86-95, 96-105
    age_brackets = {
        "13-18": 0,
        "19-25": 0,
        "26-35": 0,
        "36-45": 0,
        "46-55": 0,
        "56-65": 0,
        "66-75": 0,
        "76-85": 0,
        "86-95": 0,
        "96-105": 0,
    }
    
    for age in volunteer_ages:
        if age < 19:
            age_brackets["13-18"] += 1
        elif age < 26:
            age_brackets["19-25"] += 1
        elif age < 36:
            age_brackets["26-35"] += 1
        elif age < 46:
            age_brackets["36-45"] += 1
        elif age < 56:
            age_brackets["46-55"] += 1
        elif age < 66:
            age_brackets["56-65"] += 1
        elif age < 76:
            age_brackets["66-75"] += 1
        elif age < 86:
            age_brackets["76-85"] += 1
        elif age < 96:
            age_brackets["86-95"] += 1
        else:
            age_brackets["96-105"] += 1
            
    volunteer_data_sections.append({
        "type": "pie",
        "title": "Volunteer Age Brackets",
        "data": [{"label": key, "value": value} for key, value in age_brackets.items()]
    })
        
    try:    
        sign_up_form = Form.objects.get(sign_up_form=True)
    except Form.DoesNotExist:
        sign_up_form = None
    
    if sign_up_form:
        
        gender_makeup = {}
        gender_question = Question.objects.filter(form=sign_up_form, question="Gender", question_type="radio")
        if gender_question:
            choices = Options.objects.filter(question=gender_question)
            for choice in choices:
                gender_makeup[choice.option] = 0
                
            if organisation:
                responses = Response.objects.filter(form=sign_up_form, user__in=[reg.volunteer.user for reg in Registration.objects.filter(opportunity__organisation=organisation)])
            else:
                responses = Response.objects.filter(form=sign_up_form)
            
            for response in responses:
                answer = Answer.objects.get(response=response)
                gender_makeup[answer.answer] += 1
            
            volunteer_data_sections.append({
                "type": "pie",
                "title": "Volunteer gender makeup",
                "data": [{"label": key, "value": value} for key, value in gender_makeup.items()]
            })
            
            
        ethnicity_makeup = {}
        ethnicity_question = Question.objects.filter(form=sign_up_form, question="Ethnic Origin", question_type="radio")
        if ethnicity_question:
            choices = Options.objects.filter
            for choice in choices:
                ethnicity_makeup[choice.option] = 0
                
            if organisation:
                responses = Response.objects.filter(form=sign_up_form, user__in=[reg.volunteer.user for reg in Registration.objects.filter(opportunity__organisation=organisation)])
            else:
                responses = Response.objects.filter(form=sign_up_form)
            
            for response in responses:
                answer = Answer.objects.get(response=response)
                ethnicity_makeup[answer.answer] += 1
                
            volunteer_data_sections.append({
                "type": "pie",
                "title": "Volunteer ethnicity makeup",
                "data": [{"label": key, "value": value} for key, value in ethnicity_makeup.items()]  
            })
            
    for section in volunteer_data_sections:
        section["id"] = ''.join(random.choices(string.ascii_uppercase, k=10))
            
    print (volunteer_data_sections)
    return volunteer_data_sections
            
def get_opportunity_data(request, organisation_id=None):
    
    if request.user.is_superuser and organisation_id:
        organisation = Organisation.objects.get(id=organisation_id)
    elif not request.user.is_superuser:
        organisation = OrganisationAdmin.objects.get(user=request.user).organisation
    else:
        organisation = None
        
    opportunity_data_sections = []
    
    if organisation:
        print (organisation)
    else:
        print ("No organisation")
    
    #Opportunities with sign up that are awaiting approval
    if organisation:
        awaiting_approval = VolunteerRegistrationStatus.objects.filter(registration__opportunity__organisation=organisation, registration_status__status="Awaiting Approval")
    else:
        awaiting_approval = VolunteerRegistrationStatus.objects.filter(registration_status__status="Awaiting Approval")
    
    registrations = Registration.objects.filter(id__in=[reg.registration.id for reg in awaiting_approval])
    
    opportunities_needing_attention = {}
    
    for reg in awaiting_approval:
        if reg.opportunity not in opportunities_needing_attention:
            opportunities_needing_attention[reg.opportunity] = 0
        opportunities_needing_attention[reg.opportunity] += 1
        
    opportunity_data_sections.append({
        "type": "list",
        "title": "Opportunities needing attention",
        "data": [{"label": key.name, "value": value, "href": f"/org_admin/opportunities/{key.id}/"} for key, value in opportunities_needing_attention.items()]
    })
        
    #Opportunity views
    if organisation:
        organisation_opportunities = Opportunity.objects.filter(organisation=organisation)
    else:
        organisation_opportunities = Opportunity.objects.all()

    
    current_month = datetime.datetime.now().month
    current_year = datetime.datetime.now().year
    
        
    for opp in organisation_opportunities:
        opportunity_views_per_month = {}
        #get all views for this opportunity for the last 12 months
        for i in range(12):
            month = current_month - i
            year = current_year
            if month < 1:
                month = 12 + month
                year -= 1
            opportunity_views_per_month[f"{month}/{year}"] = OpportunityView.objects.filter(opportunity=opp, time__month=month, time__year=year).count()
            
        opportunity_data_sections.append({
            "type": "bar",
            "title": f"Views for {opp.name}",
            "data": [{"label": key, "value": value} for key, value in opportunity_views_per_month.items()]
        })
        
    expiring = []
    
    if organisation:
        opportunities = Opportunity.objects.filter(organisation=organisation)
    else:
        opportunities = Opportunity.objects.all()
    
    for opp in opportunities:
        if opp.recurrences.dtend:
            if opp.recurrences.dtend < datetime.datetime.now() + datetime.timedelta(days=30):
                expiring.append(opp)

    
    opportunity_data_sections.append({
        "type" : "list",
        "title": "Opportunities soon to expire",
        "data": [{"label": opp.name, 
                  "value": opp.recurrences.dtend,
                    "href": f"/org_admin/opportunities/{opp.id}/"
                  } for opp in expiring]
    })
    
    
    for section in opportunity_data_sections:
        section["id"] = ''.join(random.choices(string.ascii_uppercase, k=10))
        
    return opportunity_data_sections


    

def get_org_admin_data(request, organisation_id=None):
    
    if request.user.is_superuser:
        organisation = Organisation.objects.get(id=organisation_id)
    else:
        organisation = OrganisationAdmin.objects.get(user=request.user).organisation
    
    
    key_data_sections = []
    
    #key data - Organisation Views, Volunteer followers, Sign ups
    org_views = OrganisationView.objects.filter(organisation=organisation).count()
    
    key_data_sections.append({
        "type": "numeric",
        "title": "Organisation Views",
        "value": org_views,
    })
    
    org_followers = OrganisationInterest.objects.filter(organisation=organisation).count()
    
    key_data_sections.append({
        "type": "numeric",
        "title": "Organisation Followers",
        "value": org_followers,
    })
    
    org_sign_ups = Registration.objects.filter(opportunity__organisation=organisation).count()
    
    key_data_sections.append({
        "type": "numeric",
        "title": "Organisation Sign Ups",
        "value": org_sign_ups,
    })
    

    
    #add an random id to each section
    for section in key_data_sections:
        section["id"] = ''.join(random.choices(string.ascii_uppercase, k=10))
        
    
    return {
    "Key Data": key_data_sections,
    "Volunteer Data": get_volunteer_data(request, organisation_id),
    "Opportunity Data": get_opportunity_data(request, organisation_id),
    "Mentor Data": get_mentor_data(request, organisation_id),
    }
    
    
def get_chipin_admin_data(request):
    #Key data - Sign ups to platform, viewers of platform, active volunteers, active organisations, active opportunities, number of enquiries
    key_data_sections = []
    
    try:
        sign_up_form = Form.objects.get(sign_up_form=True)
    except Form.DoesNotExist:
        sign_up_form = None
    
    if sign_up_form:
        sign_ups = Response.objects.filter(form=sign_up_form)
        sign_up_count = sign_ups.count()
        
        #users that are not org admins or superusers or volunteers
        viewers = User.objects.all().count()
        org_admins = OrganisationAdmin.objects.all()
        superusers = User.objects.filter(is_superuser=True)
        
        #deduplicate org admins and superusers
        admins_count = org_admins.count() + superusers.count()
        
        #remover admins and superusers from sign up count
        for sign in sign_ups:
            if sign.user in superusers:
                sign_up_count -= 1
            if sign.user in org_admins:
                sign_up_count -= 1
            
        
        for admin in org_admins:
            if admin.user in superusers:
                admins_count -= 1
                
        print(
             f"Viewers: {viewers}\n"
            f"Sign ups: {sign_up_count}\n"
            f"Admins: {admins_count}\n"
            
        )
        
        
        
        viewers = viewers - sign_up_count - admins_count 
        

        registrations = Registration.objects.filter()
        active_registrations = [registration for registration in registrations if registration.get_registration_status() == "active"]
        
        active_volunteers = len(set([registration.volunteer for registration in active_registrations]))
        active_organisations = Organisation.objects.filter().count()
        active_opportunities = Opportunity.objects.filter(active=True).count()
        
        key_data_sections.append({
            "type": "numeric",
            "title": "Sign Ups",
            "value": sign_up_count,
        })
        
        key_data_sections.append({
            "type": "numeric",
            "title": "Viewers",
            "value": viewers,
        })
        
        key_data_sections.append({
            "type": "numeric",
            "title": "Active Volunteers",
            "value": active_volunteers,
        })
        
        key_data_sections.append({
            "type": "numeric",
            "title": "Active Organisations",
            "value": active_organisations,
        })
        
        key_data_sections.append({
            "type": "numeric",
            "title": "Active Opportunities",
            "value": active_opportunities,
        })
        
    for section in key_data_sections:
        section["id"] = ''.join(random.choices(string.ascii_uppercase, k=10))
        
    return {
        "Key Data": key_data_sections,
        "Volunteer Data": get_volunteer_data(request),
        "Opportunity Data": get_opportunity_data(request),
        "Mentor Data": get_mentor_data(request),
    }