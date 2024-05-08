from django.shortcuts import render
from forms.models import Form, Question, Options, Answer, Response
from commonui.views import check_if_hx

def forms(request):
    if request.user.is_superuser:
        forms = Form.objects.all()
    else:
        forms = Form.objects.filter(organisation=request.user.organisation)
    
    for form in forms:
        responses = Response.objects.filter(form=form)
        form.responses = responses.count()    
    
    context = {
        "forms": forms,
        "hx": check_if_hx(request),
        "superuser": request.user.is_superuser,
    }
    return render(request, 'org_admin/forms.html', context=context)

def update_form(request, form_id):
    data = request.POST
    form = Form.objects.get(pk=form_id)
    form.name = data["name"]
    

def create_form(request):
    form = Form.objects.create(name='New Form', description='Description')
    return form_detail(request, form.id)

def form_detail(request, form_id):
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
    return render(request, 'org_admin/form_details.html', context=context)

def add_multi_choice(request, form_id):
    form = Form.objects.get(pk=form_id)
    question = Question.objects.create(form=form, index=Question.objects.filter(form=form).count(), question_type='multi_choice')
    Options.objects.create(question=question, option='Option 1')
    return form_detail(request, form_id)

def add_question(request, form_id, boolean=False):
    form = Form.objects.get(pk=form_id)
    if not boolean:
        question = Question.objects.create(form=form, index=Question.objects.filter(form=form).count(), question_type='text')
    else:
        question = Question.objects.create(form=form, index=Question.objects.filter(form=form).count(), question_type='boolean')
    return form_detail(request, form_id)

def save_question(request, question_id):
    data = request.POST
    print(data)
    question = Question.objects.get(pk=question_id)
    question.question = data["question"]
    question.required = True if "required" in data.keys() else False
    question.save()
    return form_detail(request, question.form.id)

def delete_question(request, question_id):
    question = Question.objects.get(pk=question_id)
    form_id = question.form.id
    question.delete()
    return form_detail(request, form_id)

def add_option(request, question_id):
    data = request.POST
    question = Question.objects.get(pk=question_id)
    Options.objects.create(question=question, option=data["option"])
    return form_detail(request, question.form.id)

def delete_option(request, option_id):
    option = Options.objects.get(pk=option_id)
    question_id = option.question.id
    option.delete()
    return form_detail(request, question_id)