"""
VolunteeringSystem

This project is distributed under the CC BY-NC-SA 4.0 license. See LICENSE for details.
"""

from django.shortcuts import render
from django.http import HttpResponse as HTTPResponse
from commonui.views import check_if_hx
from .models import Form, Question, Options, Answer, Response, FormResponseRequirement, OrganisationFormResponseRequirement, SuperForm, SuperFormRegistration
from volunteer.views import index

from volunteer.models import Volunteer, VolunteerAddress
from opportunities.models import Opportunity, Registration, RegistrationStatus, VolunteerRegistrationStatus
from org_admin.models import OrganisationAdmin
from django.contrib.auth.models import User

def pretty_print_dict(d):
    """Pretty prints a dictionary"""
    print("--" * 20)
    for key, value in d.items():
        print(f"{key}: {value}")
    print("--" * 20)

def superform(request, id):
    """Superforms allow users to create an account, register for an opportunity, and fill out a form all at once. This allows incremental onboarding of users.
    """
    try:
        superform = SuperForm.objects.get(pk=id)
    except:
        return render (request, 'forms/superform/404.html', context={})
    if superform.active == False:
        return render (request, 'forms/superform/form_closed.html', context={})
    
    forms_to_complete = superform.forms_to_complete.all()
    forms = Form.objects.filter(id__in=forms_to_complete)
    
    formsets = []
    
    for form in forms:
        question_objects = Question.objects.filter(form=form).order_by('index')
        
        questions = []
        for question in question_objects:
            questions.append({
                "question": question,
                "options": Options.objects.filter(question=question),
            })
            
        formsets.append({
            "form": form,
            "questions": questions,
        })
        
    context = {
        "superform": superform,
        "forms": formsets,
        "hx": check_if_hx(request),
    }
    
    return render(request, 'forms/superform/form.html', context=context) 

    
    #get email and create user if not exists
    
    #Create and update formResponseRequirements and formResponses
    
    
def submit_superform(request, id):
    if request.method == 'POST':
        # Handle form submission
        superform = SuperForm.objects.get(pk=id)
        
        # Get the forms to complete
        forms_to_complete = superform.forms_to_complete.all()
        
        form_data = {}
        
        """
        Frm data in format:
        {
            "form_id": {
                "question_id": "answer"
            }
        }
        """
        
        post_data = request.POST
        print("Post data", post_data)
        #each form data key is in the format sup_(form_id)_(question_id)
        for key in post_data.keys():
            if key.startswith('sup_'):
                # Extract the form ID and question ID from the key
                _, form_id, question_id = key.split('_')
                
                if form_id not in form_data:
                    form_data[form_id] = {}
                    
                # Store the answer in the form data dictionary
                
                if len(post_data.getlist(key)) == 1:
                    form_data[form_id][question_id] = post_data.get(key)
                else:
                    form_data[form_id][question_id] = post_data.getlist(key)

                
        userdata = {
            "first_name": request.POST.get('first_name'),
            "last_name": request.POST.get('last_name'),
            "preferred_name": request.POST.get('preferred_name'),
            "date_of_birth": request.POST.get('date_of_birth'),
            "preferred_contact_method": request.POST.getlist('contact_method'),
            "post_code": request.POST.get('post_code'),
            "email": request.POST.get('email'),
            "phone": request.POST.get('phone_number'),
        }
        
        pretty_print_dict(userdata)
        pretty_print_dict(form_data)
        
        
        #try to find user by email
        email = request.POST.get('email')
        if email:
            try:
                
                
                user = User.objects.get(email=email)
                print("User exists")
                if user.first_name != userdata["first_name"]:
                    user.first_name = userdata["first_name"]
                
                if user.last_name != userdata["last_name"]:
                    user.last_name = userdata["last_name"]
                    
                user.save()
                print("User saved")
                
                try:
                    
                    volunteer = Volunteer.objects.get(user=user)
                    print("Volunteer exists")
                    if volunteer.preferred_name != userdata["preferred_name"]:
                        volunteer.preferred_name = userdata["preferred_name"]
                        
                    if volunteer.date_of_birth != userdata["date_of_birth"]:
                        volunteer.date_of_birth = userdata["date_of_birth"]
                        
                    if volunteer.phone_number != userdata["phone"]:
                        volunteer.phone_number = userdata["phone"]
                        
                    if volunteer.user.email != userdata["email"]:
                        volunteer.user.email = userdata["email"]
                        
                    volunteer.save()
                    print("Volunteer saved")
                    
                    # Check if the volunteer address exists
                    try:
                        address = VolunteerAddress.objects.get(volunteer=volunteer, postcode=userdata["post_code"])
                        print("Address exists")
                    except VolunteerAddress.DoesNotExist:
                        # Create a new address if not exists
                        print("Address does not exist")
                        address = VolunteerAddress.objects.create(
                            postcode=userdata["post_code"],
                            volunteer=volunteer,
                        )
                        address.save()
                        print("Address saved")
                    
                except Volunteer.DoesNotExist:
                    # Create a new volunteer if not exists
                    print("Volunteer does not exist")
                    volunteer = Volunteer.objects.create(
                        user=user,
                        preferred_name=userdata["preferred_name"],
                        date_of_birth=userdata["date_of_birth"],
                        phone_number=userdata["phone"],
                    )
                    
                    address = VolunteerAddress.objects.create(
                        postcode=userdata["post_code"],
                        volunteer=volunteer,
                    )
                    address.save()
                    
                    volunteer.save()
                    print("Volunteer saved")
                

            except User.DoesNotExist:
                # Create a new user if not exists
                print("User does not exist")
                user = User.objects.create_user(
                    username=email,
                    email=email,
                )
                
                user.set_unusable_password()
                user.save()
                print("User saved")
                
                volunteer = Volunteer.objects.create(
                    user=user,
                    preferred_name=userdata["preferred_name"],
                    date_of_birth=userdata["date_of_birth"],
                    phone_number=userdata["phone"],
                )
                volunteer.save()
                print("Volunteer saved")
                
                address = VolunteerAddress.objects.create(
                    postcode=userdata["post_code"],
                    volunteer=volunteer,
                )
                address.save()
                print("Address saved")
                
        
            
        forms_to_complete = [form.id for form in superform.forms_to_complete.all()]
        
        print("Forms to complete", forms_to_complete)
        
        #check ids in form_data are in forms_to_complete
        for form_id in form_data.keys():
            print("Form ID", form_id, int(form_id) in forms_to_complete)
            if int(form_id) in forms_to_complete:
                print("Form ID exists")
                form = Form.objects.get(pk=form_id)
                
                #check if user has already filled the form
                if not form.allow_multiple and Response.objects.filter(form=form, user=user).exists():
                    continue
                
                #create form response requirement
                try:
                    requirement = FormResponseRequirement.objects.get(form=form, user=user, completed=False)
                except FormResponseRequirement.DoesNotExist:
                    requirement = FormResponseRequirement.objects.create(form=form, user=user)
                
                #create form response
                response = Response.objects.create(user=user, form=form)
                response.save()
                
                #create answers
                for question_id in form_data[form_id].keys():
                    question = Question.objects.get(pk=int(question_id))
                    
                    print("Question ID", question_id)
                    print("Question", question)
                    print("Answer", form_data[form_id][question_id])
                    
                    if question.question_type == "multi_choice" and question.allow_multiple and type(form_data[form_id][question_id]) == list:
                        csv = ",".join(form_data[form_id][question_id])
                        
                        Answer.objects.create(
                            question=question,
                            answer=csv,
                            response=response,
                        ).save()
                        print("Answer saved")
                        
                    else:
                        Answer.objects.create(
                            question=question,
                            answer=form_data[form_id][question_id],
                            response=response,
                        ).save()
                        print("Answer saved")
                
                #mark requirement as completed
                requirement.completed = True
                requirement.save()
        else:
            print("Form ID does not exist")
                
        # Create a opportunity registration
        if superform.opportunity_to_register:
            opportunity = Opportunity.objects.get(pk=superform.opportunity_to_register.id)
            
            try:
                registration = Registration.objects.get(volunteer=volunteer, opportunity=opportunity)
                print("Registration exists")
                
                if registration.get_registration_status() == "stopped":
                    
                    # Create a new registration
                    registration = Registration.objects.create(
                        volunteer=volunteer,
                        opportunity=opportunity,
                    )
                    
                    # Create a new registration status
                    registration_status = VolunteerRegistrationStatus.objects.create(
                        registration=registration,
                        registration_status=RegistrationStatus.objects.get(status="awaiting_approval"),
                    )
                    
                    # Save the registration status
                    registration_status.save()
                    # Save the registration
                    registration.save()
            
                    
            except Registration.DoesNotExist:
            
                # Create a new registration
                registration = Registration.objects.create(
                    volunteer=volunteer,
                    opportunity=opportunity,
                )
                
                # Create a new registration status
                registration_status = VolunteerRegistrationStatus.objects.create(
                    registration=registration,
                    registration_status=RegistrationStatus.objects.get(status="awaiting_approval"),
                )
                
                # Save the registration status
                registration_status.save()
                # Save the registration
                registration.save()
            
            
        superform_registration = SuperFormRegistration.objects.create(
            user=user,
            superform=superform,
        )
        superform_registration.save()
        print("Superform registration saved")
        
        completion_message = superform.submitted_message if superform.submitted_message else "Thank you for completing the form. You will be contacted shortly."
        
        success_context = {
            "submission_message" : completion_message,
        }
        
        # Redirect to success page or show success message
        return render(request, 'forms/superform/submitted.html', context=success_context)
    

# Create your views here.
def fill_form(request, form_id, custom_respondee=False):
    print("custom_user_respondee",custom_respondee)
    form = Form.objects.get(pk=form_id)
    question_objects = Question.objects.filter(form=form).order_by('index')
    
    if not form.filled_by_organisation:
        allowed_to_fill = FormResponseRequirement.objects.get(form=form, user=request.user, completed=False) if FormResponseRequirement.objects.filter(form=form, user=request.user, completed=False).exists() else None
        responses = Response.objects.filter(form=form, user=request.user)
    else:
        try:
            organisation = OrganisationAdmin.objects.get(user=request.user).organisation
            
            allowed_to_fill = OrganisationFormResponseRequirement.objects.get(form=form, organisation=organisation, completed=False) if OrganisationFormResponseRequirement.objects.filter(form=form, organisation=organisation, completed=False).exists() else None
            
            organisation_admin_users = OrganisationAdmin.objects.filter(organisation=organisation).values_list('user', flat=True)
            responses = Response.objects.filter(form=form, user__in=organisation_admin_users)
        except:
            allowed_to_fill = None


    if not form.allow_multiple and responses.exists() and allowed_to_fill:
        
        if custom_respondee:
            allowed_to_fill = FormResponseRequirement.objects.get(form=form, user=User.objects.get(id=custom_respondee), completed=False)
        
        allowed_to_fill.completed = True
        allowed_to_fill.save()
        return index(request)

    
    if not allowed_to_fill and not custom_respondee:
        print("You are not allowed to fill this form")
        return index(request)
    
    questions = []
    for question in question_objects:
        questions.append({
            "question": question,
            "options": Options.objects.filter(question=question),
        })
        
    context = {
        "form": form,
        "questions": questions,
        "hx": check_if_hx(request),
        "custom_respondee": custom_respondee,
    }
    
    if OrganisationAdmin.objects.filter(user=request.user).exists():
        return render(request, 'forms/admin_fill_org_from.html', context=context)
    return render(request, 'forms/render_form.html', context=context)


def submit_response(request, form_id, custom_redirect=None, override_respondee=None):
    print(request.POST)
    errors = []
    
    form_questions = Question.objects.filter(form=Form.objects.get(pk=form_id))
    for question in form_questions:
        if question.required and not request.POST.get(str(question.pk)):
            errors.append(f"{question.question} is required")
    
    if errors:#if there are errors
        return render (request, 'forms/errors.html', context={"errors": errors})
    
    requirement = None
    
    if not Form.objects.get(pk=form_id).filled_by_organisation:
        try:
            if override_respondee:
                user = User.objects.get(id=override_respondee)
                requirement = FormResponseRequirement.objects.get(form=Form.objects.get(pk=form_id), user=user, completed=False)
                
                #check if requsting user is org admin or admin of the users volunteer org
                org = OrganisationAdmin.objects.get(user=request.user).organisation
                vol_org = Registration.objects.filter(volunteer=Volunteer.objects.get(user=user), opportunity__in=Opportunity.objects.filter(organisation = org))
                
                if len(vol_org) == 0 and request.user.is_superuser == False:
                    return render(request, 'forms/redirect_profile.html')
                
                
            requirement = FormResponseRequirement.objects.get(form=Form.objects.get(pk=form_id), user=request.user, completed=False)
        except FormResponseRequirement.DoesNotExist:
            return render(request, 'forms/redirect_profile.html')
    else:
        if not OrganisationAdmin.objects.filter(user=request.user).exists():
            return render(request, 'forms/redirect_profile.html')
        
        
        requirement = OrganisationFormResponseRequirement.objects.get(form=Form.objects.get(pk=form_id), organisation=OrganisationAdmin.objects.get(user=request.user).organisation, completed=False) if OrganisationFormResponseRequirement.objects.filter(form=Form.objects.get(pk=form_id), organisation=OrganisationAdmin.objects.get(user=request.user).organisation, completed=False).exists() else None
        
        if not requirement.exists():
            return render(request, 'forms/redirect_profile.html')
            
    response = None
    
    if override_respondee:
        user = User.objects.get(id=override_respondee)
        response = Response.objects.create(user=user, form=Form.objects.get(pk=form_id))
    else:
        response = Response.objects.create(user=request.user, form=Form.objects.get(pk=form_id))
    
    
    for question in form_questions:
        
        
        if question.question_type == "multi_choice" and question.allow_multiple and len(request.POST.getlist(str(question.pk))) > 1:
            
            csv = ",".join(request.POST.getlist(str(question.pk)))
            
            Answer.objects.create(
                question=question,
                answer=csv,
                response=response,
            )
        else:
            Answer.objects.create(
                question=question,
                answer=request.POST.get(str(question.pk)),
                response=response,
            )
    

    requirement.completed = True
    requirement.save()

    if custom_redirect:
        return

    if OrganisationAdmin.objects.filter(user=request.user).exists():
        return render(request, 'forms/redirect_admin.html')

    return render(request, 'forms/redirect_profile.html')
