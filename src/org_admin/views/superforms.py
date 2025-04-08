from forms.models import SuperForm, Form
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from opportunities.models import Opportunity
from commonui.views import check_if_hx



def superforms(request, error=None, success=None):
    
    if request.user.is_anonymous or request.user.is_superuser: return redirect('sign_in')
    
    context = {
        "hx": check_if_hx(request),
        "superforms": SuperForm.objects.all(),
        "error": error,
        "success": success,
    }
    return render(request, 'org_admin/superforms/manage_superforms.html', context=context)

def new_superform(request):
    
    if request.user.is_anonymous or request.user.is_superuser: return redirect('sign_in')
    
    if request.method == 'POST':
        # Handle form submission
    
        
        superform_name = request.POST.get('name')
        superform_description = request.POST.get('description')
        superform_submitted_message = request.POST.get('submitted_message')
        
        superform_active = request.POST.get('is_active')
        superform_active = True if superform_active == 'on' else False
        
        superform_show_form_titles = request.POST.get('show_form_titles')

        superform_show_form_titles = True if superform_show_form_titles == 'on' else False
        
        superform_show_form_descriptions = request.POST.get('show_form_descriptions')
        superform_show_form_descriptions = True if superform_show_form_descriptions == 'on' else False
        # Create a new SuperForm instance
        
        superform_opportunity = request.POST.get('opportunity')
        superform_opportunity = Opportunity.objects.get(id=superform_opportunity)
        
        superform_forms = request.POST.getlist('required_forms')
        superform_forms = Form.objects.filter(id__in=superform_forms)
        
        superform = SuperForm.objects.create(
            name=superform_name,
            description=superform_description,
            submitted_message=superform_submitted_message,
            active=superform_active,
            show_form_descriptions = superform_show_form_descriptions,
            show_form_titles = superform_show_form_titles,
            opportunity_to_register=superform_opportunity
            
        )
        
        superform.forms_to_complete.set(superform_forms)
        
        superform.save()
        
        return superforms(request, success="Superform created successfully")
    else:
        return edit_superform(request)

def edit_superform(request, superform_id=None):
    
    if request.user.is_anonymous or request.user.is_superuser: return redirect('sign_in')
    
    if request.method == "POST":
        # Handle form submission
        superform_name = request.POST.get('name')
        superform_description = request.POST.get('description')
        superform_submitted_message = request.POST.get('submitted_message')
        
        superform_active = request.POST.get('is_active')
        print(superform_active)
        superform_active = True if superform_active == 'true' else False
        
        superform_show_form_titles = request.POST.get('show_form_titles')
        superform_show_form_titles = True if superform_show_form_titles == 'true' else False
        
        superform_show_form_descriptions = request.POST.get('show_form_descriptions')
        superform_show_form_descriptions = True if superform_show_form_descriptions == 'true' else False
        
        superform_opportunity = request.POST.get('opportunity')
        superform_opportunity = Opportunity.objects.get(id=superform_opportunity)
        
        superform_forms = request.POST.getlist('required_forms')
        print(superform_forms)
        superform_forms = Form.objects.filter(id__in=superform_forms)
        
        print(superform_forms)
        
        if superform_id:
            try:
                superform = SuperForm.objects.get(id=superform_id)
                superform.name = superform_name
                superform.description = superform_description
                superform.submitted_message = superform_submitted_message
                superform.active = superform_active
                superform.show_form_titles = superform_show_form_titles
                superform.show_form_descriptions = superform_show_form_descriptions
                superform.opportunity_to_register = superform_opportunity
                superform.forms_to_complete.set(superform_forms)
                superform.save()
                
                return superforms(request, success="Superform updated successfully")
            except SuperForm.DoesNotExist:
                return superforms(request, error="Superform not found")
        else:
            return superforms(request, error="Superform ID not provided")
    
    
    if superform_id:
        try:
            superform = SuperForm.objects.get(id=superform_id)
        except SuperForm.DoesNotExist:
            return superforms(request, error="Superform not found")
    else:
        superform = None
        
    
    context = {
        "opportunities": Opportunity.objects.all(),
        "superform": superform,
        "forms": Form.objects.all(),
    }
    
    return render(request, 'org_admin/superforms/edit_superform.html', context=context)