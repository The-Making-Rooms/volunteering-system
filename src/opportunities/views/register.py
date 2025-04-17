from volunteer.models import Volunteer, SupplementaryInfo, VolunteerSupplementaryInfo
from forms.models import Form, FormResponseRequirement, Question, Options, Answer, Response
from commonui.views import check_if_hx
from org_admin.models import OrganisationAdmin

from ..models import Opportunity, Registration, RegistrationStatus, VolunteerRegistrationStatus, SupplimentaryInfoRequirement
from django.shortcuts import render, HttpResponseRedirect
from django.utils import timezone
from threading import Thread
from django.core.mail import send_mail

def check_volunteer_allowed_to_register(opportunity: Opportunity, volunteer: Volunteer):
    """
    Check if the volunteer is allowed to register for the opportunity.
    This function checks if the volunteer has already registered for the opportunity,
    and if so, whether the registration status is 'stopped'.
    
    :param opportunity: The opportunity object
    :param volunteer: The volunteer object
    :return: True if the volunteer is allowed to register, False otherwise
    """
    
    # Check if the volunteer has already registered for the opportunity
    registration = Registration.objects.filter(volunteer=volunteer, opportunity=opportunity).first()
    
    # If there is no registration, allow the volunteer to register
    if not registration:
        return True
    
    # If there is a registration, check the status
    latest_registration_status = VolunteerRegistrationStatus.objects.filter(registration=registration).order_by('-date').first()
    
    # If the latest registration status is 'stopped', allow the volunteer to register again
    if latest_registration_status and latest_registration_status.registration_status.status == 'stopped':
        return True
    
    # Otherwise, do not allow the volunteer to register
    return False
    

def register(request, opportunity_id, error=None):
    
    opportunity = None
    volunteer = None
    form = None
    questions = None
    
    # Check if the user is authenticated and redirect accordingly
    if not request.user.is_authenticated:
        return HttpResponseRedirect("/volunteer/")
    
    # Check if the user is an organisation admin and redirect accordingly
    if OrganisationAdmin.objects.filter(user=request.user).exists():
        return HttpResponseRedirect("/org_admin/")
    
    # Check if the user is a volunteer and redirect accordingly
    # If the user is not a volunteer, redirect to the volunteer page
    try:
        volunteer = Volunteer.objects.get(user=request.user)
    except Volunteer.DoesNotExist:
        return HttpResponseRedirect("/volunteer/")
    
    
    # Check if the opportunity exists and redirect accordingly
    # If the opportunity does not exist, render a 404 page
    try:
        opportunity = Opportunity.objects.get(id=opportunity_id)
    except Opportunity.DoesNotExist:
        return render(request, "404.html", status=404)
    
    
    if not opportunity or not volunteer:
        return HttpResponseRedirect("/volunteer/")
    
    # Check if the opportunity is active and redirect accordingly
    if not opportunity.active:
        return HttpResponseRedirect("/volunteer/")
    
    # Check if the volunteer is allowed to register for the opportunity
    if not check_volunteer_allowed_to_register(opportunity, volunteer):
        return HttpResponseRedirect("/volunteer/")
    
    if request.method == "POST":
        return register_opportunity(request, opportunity, volunteer)
        
    #Check if the opportunity has a form
    oppportunity_form = opportunity.form
    if oppportunity_form:
        form = Form.objects.get(id=oppportunity_form.id)
        question_objects = Question.objects.filter(form=form, enabled=True).order_by('index')
        questions = []
        for question in question_objects:
            questions.append({
                "question": question,
                "options": Options.objects.filter(question=question),
            })
    
    #check supplementary info requirements
    supplementary_info_requirements = SupplimentaryInfoRequirement.objects.filter(opportunity=opportunity)
    
    for supplementary_info_requirement in supplementary_info_requirements:
        response = VolunteerSupplementaryInfo.objects.filter(
            volunteer=volunteer,
            info=supplementary_info_requirement.info
        )
        
        if response.exists():

            supplementary_info_requirement.response = response.first()
        else:
            supplementary_info_requirement.response = None
            
            
            
        
    
    
    
    context = {
        "hx": check_if_hx(request),
        "error": error,
        "opportunity": opportunity,
        "volunteer": volunteer,
        "form": form,
        "questions": questions,
        "supplementary_info": supplementary_info_requirements,
    }
    
    return render(request, "opportunities/register/register.html", context=context)

def register_opportunity(request, opportunity: Opportunity, volunteer: Volunteer):
    """
    Register the volunteer for the opportunity.
    This function checks if the volunteer has already registered for the opportunity,
    and if so, whether the registration status is 'stopped'.
    
    :param request: The request object
    :param opportunity: The opportunity object
    :param volunteer: The volunteer object
    :return: HttpResponseRedirect to the volunteer page
    """
    
    form_data = request.POST
    
    supplimentary_form_data = {}
    form_question_responses = {}
    
    
    
    for key, value in form_data.items():
        if key.startswith("sup_"):
            supplementary_info_id = key.split("_")[1]
            supplimentary_form_data[supplementary_info_id] = value
        elif key is not "csrfmiddlewaretoken":
            question_id = key
            form_question_responses[question_id] = value
    

    if opportunity.form:
        form = Form.objects.get(id=opportunity.form.id)
        question_objects = Question.objects.filter(form=form)
        
        print("Form question responses: ", form_question_responses)
        
        for question in question_objects:
            if str(question.id) not in form_question_responses and question.required:
                print("Question not answered: ", question.id)
                # If the question is required and not answered, return an error
                request.method = "GET"
                return register(request, opportunity.id, error="Please answer all required questions.")
            
        #create a form response requirement 
        form_response = FormResponseRequirement.objects.create(
            form=form,
            user=volunteer.user,
    
        )
        
        print("Form response requirement: ", form_response)
        
        #Create the form response
        response_object = Response.objects.create(
            user=volunteer.user,
            form=form
        )
        
        print("Response object: ", response_object)
        
        for question in question_objects:
            print("Question: ", question)
            
            if str(question.id) in form_question_responses:
                answer = form_question_responses[str(question.id)]
                Answer.objects.create(
                    question=question,
                    response=response_object,
                    answer=answer
                )
                print("Answer created: ", answer)
            else:
                print(question.id, " not in", form_question_responses)
                
        form_response.completed = True
        form_response.save()
        
    # Create the supplementary info responses
    for supplementary_info_id, response in supplimentary_form_data.items():
        try:
            supplementary_info = SupplementaryInfo.objects.get(id=supplementary_info_id)
            
            if VolunteerSupplementaryInfo.objects.filter(volunteer=volunteer, info=supplementary_info).exists():
                # If the response already exists, update it
                volunteer_supplementary_info = VolunteerSupplementaryInfo.objects.get(volunteer=volunteer, info=supplementary_info)
                volunteer_supplementary_info.data = response
                volunteer_supplementary_info.last_updated = timezone.now()
                volunteer_supplementary_info.save()
            else:
                # If the response does not exist, create it
                volunteer_supplementary_info = VolunteerSupplementaryInfo.objects.create(
                    volunteer=volunteer,
                    info=supplementary_info,
                    data=response,
                    last_updated=timezone.now(),
                )
            
        except SupplementaryInfo.DoesNotExist:
            # Handle the case where the supplementary info does not exist
            pass
        
    # Create the registration
    registration = Registration.objects.create(
        volunteer=volunteer,
        opportunity=opportunity,
    )
    
    # Create the registration status
    VolunteerRegistrationStatus.objects.create(
        registration=registration,
        registration_status=RegistrationStatus.objects.get(status="awaiting_approval"),
    )
    
    # Send email to organisation admins
    send_email_thread = SendEmailToOrgAdminsThread(request, opportunity.id)
    send_email_thread.start()
    
    # Redirect to the volunteer opportunities page
    return HttpResponseRedirect("/volunteer/your-opportunities/")
    
                
        
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