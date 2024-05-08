from django.shortcuts import render
from commonui.views import check_if_hx
from .models import Form, Question, Options, Answer, Response
# Create your views here.
def fill_form(request, form_id):
    form = Form.objects.get(pk=form_id)
    question_objects = Question.objects.filter(form=form)
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
