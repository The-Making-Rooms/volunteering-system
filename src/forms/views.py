from django.shortcuts import render
from django.http import HttpResponse as HTTPResponse
from commonui.views import check_if_hx
from .models import Form, Question, Options, Answer, Response, FormResponseRequirement
from volunteer.views import index
from org_admin.models import OrganisationAdmin
# Create your views here.
def fill_form(request, form_id):
    form = Form.objects.get(pk=form_id)
    question_objects = Question.objects.filter(form=form).order_by('index')
    
    if not form.filled_by_organisation:
        allowed_to_fill = FormResponseRequirement.objects.get(form=form, user=request.user, completed=False) if FormResponseRequirement.objects.filter(form=form, user=request.user, completed=False).exists() else None
    else:
        allowed_to_fill = len(OrganisationAdmin.objects.filter(user=request.user)) > 0
    
    responses = Response.objects.filter(form=form, user=request.user)
    
    if not form.allow_multiple and responses.exists() and allowed_to_fill:
        allowed_to_fill.completed = True
        allowed_to_fill.save()
        return index(request)
    
    if not allowed_to_fill:
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
    }
    
    if OrganisationAdmin.objects.filter(user=request.user).exists():
        return render(request, 'forms/admin_fill_org_from.html', context=context)
    return render(request, 'forms/render_form.html', context=context)


def submit_response(request, form_id):
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
            requirement = FormResponseRequirement.objects.get(form=Form.objects.get(pk=form_id), user=request.user, completed=False)
        except FormResponseRequirement.DoesNotExist:
            return render(request, 'forms/redirect_profile.html')
    else:
        if len(OrganisationAdmin.objects.filter(user=request.user)) == 0:
            return render(request, 'forms/redirect_profile.html')
    
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
    
    if not Form.objects.get(pk=form_id).filled_by_organisation:        
        requirement.completed = True
        requirement.save()


    if OrganisationAdmin.objects.filter(user=request.user).exists():
        return render(request, 'forms/redirect_admin.html')
    return render(request, 'forms/redirect_profile.html')
