"""
VolunteeringSystem

This project is distributed under the CC BY-NC-SA 4.0 license. See LICENSE for details.
"""

from django.shortcuts import render
from django.http import HttpResponse as HTTPResponse
from commonui.views import check_if_hx
from .models import Form, Question, Options, Answer, Response, FormResponseRequirement, OrganisationFormResponseRequirement
from volunteer.views import index

from volunteer.models import Volunteer
from opportunities.models import Opportunity, Registration
from org_admin.models import OrganisationAdmin
from django.contrib.auth.models import User
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
