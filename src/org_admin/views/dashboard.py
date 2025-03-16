from django.shortcuts import render
from commonui.views import check_if_hx
import random
import string
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
        "sections": get_org_admin_data(request, 1005),
    }
    return render(
        request,
        "org_admin/dashboard.html",
        context=context,
    )
    
    
def get_org_admin_data(request, organisation_id=None):
    
    if request.user.is_superuser:
        organisation = Organisation.objects.get(id=organisation_id)
    else:
        organisation = OrganisationAdmin.objects.get(user=request.user).organisation
    
    data_sections = []
    
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
    
    
    #Volunteer data - Volunteer age brackets, gender make up, ethnicity make up
    volunteer_data_sections = []
    
    volunteer_dobs = [reg.volunteer.date_of_birth for reg in Registration.objects.filter(opportunity__organisation=organisation)]
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
            
    sign_up_form = Form.objects.get(sign_up_form=True)
    
    if sign_up_form:
        
        gender_makeup = {}
        gender_question = Question.objects.filter(form=sign_up_form, question="Gender", question_type="radio")
        if gender_question:
            choices = Options.objects.filter(question=gender_question)
            for choice in choices:
                gender_makeup[choice.option] = 0
            responses = Response.objects.filter(form=sign_up_form, user__in=[reg.volunteer.user for reg in Registration.objects.filter(opportunity__organisation=organisation)])
            
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
            responses = Response.objects.filter(form=sign_up_form, user__in=[reg.volunteer.user for reg in Registration.objects.filter(opportunity__organisation=organisation)])
            
            for response in responses:
                answer = Answer.objects.get(response=response)
                ethnicity_makeup[answer.answer] += 1
                
            volunteer_data_sections.append({
                "type": "pie",
                "title": "Volunteer ethnicity makeup",
                "data": [{"label": key, "value": value} for key, value in ethnicity_makeup.items()]  
            })
            
            
    #Opportunity data - Soon to expire, needs attention, views
    opportunity_data_sections = []
    opportunities = Opportunity.objects.filter(organisation=organisation)
    
    expiring = []
    
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
    
    #Opportunities with sign up that are awaiting approval
    awaiting_approval = VolunteerRegistrationStatus.objects.filter(registration__opportunity__organisation=organisation, registration_status__status="Awaiting Approval")
    
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
    organisation_opportunities = Opportunity.objects.filter(organisation=organisation)

    
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
    
    #add an random id to each section
    for section in key_data_sections:
        section["id"] = ''.join(random.choices(string.ascii_uppercase, k=10))
        
    for section in volunteer_data_sections:
        section["id"] = ''.join(random.choices(string.ascii_uppercase, k=10))
        
    for section in opportunity_data_sections:
        section["id"] = ''.join(random.choices(string.ascii_uppercase, k=10))
    
    return {
        "Key Data": key_data_sections,
        "Volunteer Data": volunteer_data_sections,
        "Opportunity Data": opportunity_data_sections,
        }
        
    
    
    #mentoring - Active mentees, running total of mentees, completed inital questionnaires, completed exit questionnaires
    
    