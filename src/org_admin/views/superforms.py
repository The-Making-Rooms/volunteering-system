from forms.models import SuperForm, Form
from django.http import HttpResponse
from django.shortcuts import render
from opportunities.models import Opportunity

def superforms(request):
    context = {
        "superforms": SuperForm.objects.all(),
    }
    return render(request, 'org_admin/superforms/manage_superforms.html', context=context)

def new_superform(request):
    if request.method == 'POST':
        # Handle form submission
        superform_name = request.POST.get('name')
        superform_description = request.POST.get('description')
        # Create a new SuperForm instance
        
        superform_opportunity = request.POST.get('opportunity')
        superform_opportunity = Opportunity.objects.get(id=superform_opportunity)
        
        superform_forms = request.POST.getlist('forms')
        superform_forms = Form.objects.filter(id__in=superform_forms)
        
        superform = SuperForm.objects.create(
            name=superform_name,
            description=superform_description,
            opportunity_to_register=superform_opportunity
        )
        
        superform.forms_to_complete.set(superform_forms)
        
        superform.save()
        
        return HttpResponse(f"SuperForm '{superform.name}' created successfully!")
    else:
        return edit_superform(request)

def edit_superform(request, superform_id=None):
    
    
    context = {
        "opportunities": Opportunity.objects.all(),
        "superform": None,
        "forms": Form.objects.all(),
    }
    
    return render(request, 'org_admin/superforms/edit_superform.html', context=context)