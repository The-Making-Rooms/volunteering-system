import io
from django.shortcuts import render
from forms.models import Form, Question, Options, Answer, Response, FormResponseRequirement, OrganisationFormResponseRequirement
from django.contrib.auth.models import User
from commonui.views import check_if_hx
from org_admin.views import check_ownership
from org_admin.models import OrganisationAdmin
import csv
from django.http import HttpResponse
from volunteer.models import Volunteer
from opportunities.models import Registration, RegistrationStatus, VolunteerRegistrationStatus, Opportunity
from organisations.models import Organisation

def check_form_ownership(request, form):
    if not request.user.is_superuser:
        if not check_ownership(request, form):
            return forms(request, error="You do not have permission to view this form")

def forms(request, error=None, success=None):
    if request.user.is_superuser:
        forms = Form.objects.all()
        assignable_forms = None
        incomplete_reqs = None
        awaiting_response = OrganisationFormResponseRequirement.objects.filter(completed=False)
    else:
        awaiting_response = None
    #Check for organisation form rsponse requirements
    
        incomplete_reqs = None
    
        try:
            organisation = OrganisationAdmin.objects.get(user=request.user).organisation
            incomplete_reqs = OrganisationFormResponseRequirement.objects.filter(organisation=organisation, completed=False)
        
        except:
            pass
            
            
        else:
            forms = Form.objects.filter(organisation=OrganisationAdmin.objects.get(user=request.user).organisation)
            assignable_forms = Form.objects.filter(visible_to_all=True)
            forms = forms | assignable_forms
        
        for form in forms:
            responses = Response.objects.filter(form=form)
            form.responses = responses.count()    
    
    context = {
        "awaiting_response": awaiting_response,
        "assigned_forms": incomplete_reqs,
        "forms": forms,
        "assignable_forms": assignable_forms,
        "hx": check_if_hx(request),
        "superuser": request.user.is_superuser,
        "error": error,
        "success": success,
    }
    return render(request, 'org_admin/forms.html', context=context)

def update_form(request, form_id):
    
    try:
        data = request.POST
        form = Form.objects.get(pk=form_id)
        
        check_form_ownership(request, form)
        
        if request.user.is_superuser:
            form.visible_to_all = True if "visible_to_all" in data.keys() else False
            form.filled_by_organisation = True if "filled_by_organisations" in data.keys() else False
        
        form.name = data["name"]
        form.description = data["description"]
        form.allow_multiple = True if "allow_multiple" in data.keys() else False
        
        form.required_on_signup = True if "required_on_signup" in data.keys() else False
        
        if request.user.is_superuser:
        
            if "mentor_start_form" in data.keys():
                forms = Form.objects.filter()
                for uform in forms: uform.mentor_start_form = False
                form.mentor_start_form = True
            else:
                form.mentor_start_form = False
                    
            if "mentor_end_form" in data.keys():
                forms = Form.objects.filter()
                for uform in forms: uform.mentor_end_form = False
                form.mentor_end_form = True
            else:
                form.mentor_end_form = False
        
        form.save()
        return form_detail(request, form_id, success="Form Updated")
    
    except Exception as e:
        print(e)
        return form_detail(request, form_id, error="Error updating form")
    
def delete_form(request, form_id):
    if request.method == "GET":
        check_form_ownership(request, Form.objects.get(pk=form_id))
        req_form = Form.objects.get(pk=form_id)
        context = {
            "form_name" : req_form.name,
            "responses" : Response.objects.filter(form=req_form).count(),
            "form_id" : form_id,
            "hx" : check_if_hx(request),
        }
        return render(request, 'org_admin/form_delete_confirm.html', context=context)
    else:    
        form = Form.objects.get(pk=form_id)
        check_form_ownership(request, form)
        form.delete()
        return forms(request, success="Form Deleted")

def create_form(request):
    if not request.user.is_superuser:
        organisation = OrganisationAdmin.objects.get(user=request.user).organisation
    else:
        organisation = None
    form = Form.objects.create(name='New Form', description='', organisation=organisation)
    return form_detail(request, form.id)

def form_detail(request, form_id, success=None, error=None):
    form = Form.objects.get(pk=form_id)
    
    check_form_ownership(request, form)
        
        
    question_objects = Question.objects.filter(form=form).order_by('index')
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
        "success": success,
        "error": error,
        "superuser": request.user.is_superuser,
    }
    return render(request, 'org_admin/form_details.html', context=context)

def add_multi_choice(request, form_id):
    form = Form.objects.get(pk=form_id)
    
    check_form_ownership(request, form)
    
    question = Question.objects.create(form=form, index=Question.objects.filter(form=form).count(), question_type='multi_choice')
    return form_detail(request, form_id, success="Multi Choice Question Added")

def add_question(request, form_id, boolean=False):
    form = Form.objects.get(pk=form_id)
    
    check_form_ownership(request, form)
        
        
    if not boolean:
        question = Question.objects.create(form=form, index=Question.objects.filter(form=form).count(), question_type='text')
    else:
        question = Question.objects.create(form=form, index=Question.objects.filter(form=form).count(), question_type='boolean')
    return form_detail(request, form_id, success="Question Added")

def duplicate_question(request, question_id):
    question = Question.objects.get(pk=question_id)
    form = question.form
    
    check_form_ownership(request, form)
    
    new_question = Question.objects.create(form=form, index=Question.objects.filter(form=form).count(), question=question.question, question_type=question.question_type, required=question.required, allow_multiple=question.allow_multiple)
    
    if question.question_type == 'multi_choice':
        for option in Options.objects.filter(question=question):
            Options.objects.create(question=new_question, option=option.option)
    
    return form_detail(request, form.id, success="Question Duplicated")

def save_question(request, question_id):
    data = request.POST
    print(data)
    question = Question.objects.get(pk=question_id)
    form = question.form
    
    check_form_ownership(request, form)

    
    question.enabled = True if not "hidden" in data.keys() else False
    question.question = data["question"]
    question.required = True if "required" in data.keys() else False
    question.allow_multiple = True if "allow_multiple" in data.keys() else False

    question.save()
    return form_detail(request, question.form.id, success="Question Updated")

def delete_question(request, question_id):
    question = Question.objects.get(pk=question_id)
    
    form = question.form
    
    check_form_ownership(request, form)
    
    responses = Response.objects.filter(form=form)
    
    if responses.count() > 0:
        return form_detail(request, form.id, error="Cannot delete question with responses")
        
    form_id = question.form.id
    question.delete()
    return form_detail(request, form_id, success="Question Deleted")

def add_option(request, question_id):
    data = request.POST
    question = Question.objects.get(pk=question_id)
    form = question.form
    
    check_form_ownership(request, form)
        
    Options.objects.create(question=question, option=data["option"])
    return form_detail(request, question.form.id, success="Option Added")

def delete_option(request, option_id):
    option = Options.objects.get(pk=option_id)
    form_id = option.question.form.id
    form = option.question.form
    check_form_ownership(request, form)
    
    responses = Response.objects.filter(form=form)
    
    if responses.count() > 0:
        return form_detail(request, form.id, error="Cannot delete question with responses")
    
    option.delete()
    return form_detail(request, form_id, success="Option Deleted")

def get_responses(request, form_id):
    form = Form.objects.get(pk=form_id)
    if not request.user.is_superuser:
        if form.organisation != OrganisationAdmin.objects.get(user=request.user).organisation:
            return forms(request, error="You do not have permission to view this form")
    responses = Response.objects.filter(form=form)
    
    context = {
        "responses": responses,
        "form": form,
        "hx": check_if_hx(request),
    }
    
    return render(request, 'org_admin/form_responses.html', context=context)

def get_response(request, response_id):
    response = Response.objects.get(pk=response_id)
    form = response.form
    
    check_form_ownership(request, form)
    
    answers = []
    
    for answer in Answer.objects.filter(response=response):
        
        options = None
        
        if answer.question.question_type == 'multi_choice' and answer.answer != "":
            
            if answer.answer != None and "," in answer.answer:
                print("multi")
                print(answer.answer)
                answer.answer = answer.answer.split(",")
                options = []
                try:
                    for option in answer.answer:
                        options.append(Options.objects.get(pk=option))
                except:
                    pass
                
                print(options)
                
                answers.append({
                    "answer": answer,
                    "option": options,
                })
            else:
                print("radio")
                options = []
                try:
                    options.append(Options.objects.get(pk=answer.answer))
                except:
                    pass
                answers.append({
                    "answer": answer,
                    "option": options,
                })
        else:
            answers.append({
                "answer": answer,
            })
        
    context = {
        "form": form,
        "response": response,
        "answers": answers,
        "hx": check_if_hx(request),
    }
    
    return render(request, 'org_admin/form_response.html', context=context)


def reindex_questions(form):
    questions = Question.objects.filter(form=form).order_by('index')
    for index, question in enumerate(questions):
        question.index = index
        question.save()
    return questions

def move_question_up(request, question_id):
    question = Question.objects.get(pk=question_id)
    form = question.form
    
    check_form_ownership(request, form)
        
    questions = reindex_questions(form)
    index = question.index
    if index > 0:
        question.index = index - 1
        question.save()
        questions[index - 1].index = index
        questions[index - 1].save()
    return form_detail(request, form.id)

def move_question_down(request, question_id):
    question = Question.objects.get(pk=question_id)
    form = question.form
    
    check_form_ownership(request, form)
        
    questions = reindex_questions(form)
    index = question.index
    if index < len(questions) - 1:
        question.index = index + 1
        question.save()
        questions[index + 1].index = index
        questions[index + 1].save()
    return form_detail(request, form.id)

def download_responses_CSV(request, form_id, anonymous=False):
    form = Form.objects.get(pk=form_id)
    check_form_ownership(request, form)
    
    response = Response.objects.filter(form=form)
    
    if response.count() == 0:
        return forms(request, error="There are no responses to download")
    
    response_dicts = []
    
    if anonymous:
        field_names = ["response_date"]
    else:
        field_names = ["first_name", "last_name", "DOB", "email", "phone_number", "response_date"]
        
    field_names += [question.question for question in Question.objects.filter(form=form, enabled=True)]
    
    for res in response:
        answers = Answer.objects.filter(response=res)
        
        response_dict = {}
        
        if not anonymous:
            response_dict["first_name"] = res.user.first_name
            response_dict["last_name"] = res.user.last_name
            response_dict["DOB"] = Volunteer.objects.get(user=res.user).date_of_birth
            response_dict["email"] = res.user.email
            response_dict["phone_number"] = Volunteer.objects.get(user=res.user).phone_number
            
        response_dict["response_date"] = res.response_date
        
        for answer in answers:
            if answer.question.question_type == 'multi_choice':
                response_dict[answer.question.question] = []
                if answer.answer != "" and answer.answer != None:
                    for option in answer.answer.split(","):
                        response_dict[answer.question.question].append(Options.objects.get(pk=option).option)
                    response_dict[answer.question.question] = ", ".join(response_dict[answer.question.question])
                else:
                    response_dict[answer.question.question] = answer.answer
            else:
                response_dict[answer.question.question] = answer.answer
                
        response_dicts.append(response_dict)
            
    #create CSV from response_dicts
    bytes_file = io.StringIO()
    
    print(response_dicts)
    
    writer = csv.DictWriter(bytes_file, fieldnames=field_names)
    writer.writeheader()
    for response in response_dicts:
        writer.writerow(response)
        
        
    response = HttpResponse(bytes_file.getvalue(), content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="responses.csv"'
    
    return response

def assign_form_org(request):
    if request.method == "GET":
        organisations = Organisation.objects.all()
        org_forms = Form.objects.filter(filled_by_organisation=True)
        context = {
            "orgs": organisations,
            "forms": org_forms,
            "hx": check_if_hx(request),
        }
        return render(request, 'org_admin/assign_form_org.html', context=context)
    elif request.method == "POST":
        data = request.POST
        
        if not data['org_id'] == "all":  
            try:
                org = Organisation.objects.get(pk=data['org_id'])
            except:
                return forms(request, error="Organisation not found")
        
        try:
            form = Form.objects.get(pk=data['form_id'])
        
            if not form.filled_by_organisation:
                return forms(request, error="Form cannot be filled by organisation")
        except:
            return forms(request, error="Form not found")
        
        if not data['org_id'] == "all":
        
            if not form.allow_multiple:
                response = OrganisationFormResponseRequirement.objects.filter(organisation=org, form=form)
                if response.count() > 0:
                    return forms(request, error="Form already assigned to organisation. Multiple submissions not allowed")

            response = OrganisationFormResponseRequirement.objects.filter(organisation=org, form=form, completed=False)
            if response.count() > 0:
                return forms(request, error="Incomplete Form already assigned to organisation")
            
        else:
            organisations = Organisation.objects.all()
            success_count = 0
            error_count = 0
            
            for org in organisations:
                if not form.allow_multiple:
                    response = OrganisationFormResponseRequirement.objects.filter(organisation=org, form=form)
                    if response.count() > 0:
                        error_count += 1
                        continue
            
                response = OrganisationFormResponseRequirement.objects.filter(organisation=org, form=form, completed=False)
                if response.count() > 0:
                    error_count += 1
                    continue
                
                OrganisationFormResponseRequirement.objects.create(organisation=org, form=form)
                success_count += 1
                
            return forms(request, success=f"Form Assigned to {success_count} Organisations. {error_count} Errors")
        
        OrganisationFormResponseRequirement.objects.create(organisation=org, form=form)
        return forms(request, success="Form Assigned to Organisation")
    
def assign_form(request):
    if request.method == "GET":
        if request.user.is_superuser:
            volunteers = Volunteer.objects.all()
            o_forms = Form.objects.all()
        else:
            org = OrganisationAdmin.objects.get(user=request.user).organisation
            
            volunteers = []
            registrations = Registration.objects.filter(opportunity__organisation=org)
            
            for registration in registrations:
                print(registration.get_registration_status())
                if registration.get_registration_status() == "active":
                    volunteers.append(registration.volunteer)

            o_forms = Form.objects.filter(organisation=org)
            o_forms = o_forms | Form.objects.filter(visible_to_all=True)
        
        context = {
            "forms": o_forms,
            "volunteers": volunteers,
            "hx": check_if_hx(request),
        }
        
        return render(request, 'org_admin/assign_form.html', context=context)
    else:
        data = request.POST
        volunteers_selected = data.getlist('volunteer')
        form = Form.objects.get(pk=data['form_id'])
        
        print (volunteers_selected)
        errors = []
        passes = []
        
        if len(volunteers_selected) == 0:
            return forms(request, error="No Volunteers Selected")
        
        for volunteer in volunteers_selected:
            user = Volunteer.objects.get(pk=volunteer).user
            has_completed = FormResponseRequirement.objects.filter(form=form, user=user).count()
            has_incomplete = FormResponseRequirement.objects.filter(form=form, user=user, completed=False).count()
            
            print("multiple:",form.allow_multiple)
            if has_incomplete > 0 and form.allow_multiple:
                errors.append(user.first_name + " " + user.last_name + " has an incomplete form")
            elif has_incomplete > 0 and not form.allow_multiple:
                errors.append(user.first_name + " " + user.last_name + " has an incomplete form. Multiple ")
            elif has_completed > 0 and not form.allow_multiple:
                errors.append(user.first_name + " " + user.last_name + " has already completed this form")
            elif has_completed > 0 and form.allow_multiple:
                FormResponseRequirement.objects.create(form=form, user=user)
                passes.append("form assigned to " + user.first_name + " " + user.last_name)
            else:
                FormResponseRequirement.objects.create(form=form, user=user)
                passes.append("Form assigned to " + user.first_name + " " + user.last_name)
        
        print (errors)
                
        return forms(request, success=passes, error=errors)
    
def assign_form_to_user(request, form_id, user_id):
    form = Form.objects.get(pk=form_id)
    user = User.objects.get(pk=user_id)
    FormResponseRequirement.objects.create(form=form, user=user)
    return form_detail(request, form_id, success="Form Assigned to User")