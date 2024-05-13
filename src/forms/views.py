from django.shortcuts import render
from django.http import HttpResponse as HTTPResponse
from commonui.views import check_if_hx
from .models import Form, Question, Options, Answer, Response, FormResponseRequirement
from volunteer.views import index
# Create your views here.
def fill_form(request, form_id):
    form = Form.objects.get(pk=form_id)
    question_objects = Question.objects.filter(form=form).order_by('index')
    
    allowed_to_fill = FormResponseRequirement.objects.get(form=form, user=request.user, completed=False) if FormResponseRequirement.objects.filter(form=form, user=request.user, completed=False).exists() else None
    
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
            
        try:
            requirement = FormResponseRequirement.objects.get(form=Form.objects.get(pk=form_id), user=request.user, completed=False)
            requirement.completed = True
            requirement.save()
        except FormResponseRequirement.DoesNotExist:
            return render(request, 'forms/redirect_profile.html')

    return render(request, 'forms/redirect_profile.html')
