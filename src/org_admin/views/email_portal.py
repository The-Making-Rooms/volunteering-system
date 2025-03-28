from ..models import EmailDraft
from django.shortcuts import render, redirect
from django.core.mail import get_connection, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings

from org_admin.models import OrganisationAdmin
from volunteer.models import Volunteer

from commonui.views import check_if_hx
from datetime import datetime
import random
import string

from opportunities.models import Opportunity, Registration
from organisations.models import Organisation

import threading

def check_auth(request):
    if request.user.is_anonymous:
        return redirect('login')
    if not request.user.is_superuser:
        return redirect('volunteer')
    return None

def email_portal_index(request, error=None, success=None):
    check_auth(request)

    context = {
        'drafts': EmailDraft.objects.filter(sent=False),
        'sent_drafts': EmailDraft.objects.filter(sent=True),
        'hx': check_if_hx(request),
        'error': error,
        'success': success
    }
    
    return render(request, 'org_admin/email_portal/index.html', context)

def save_email_draft(request):
    check_auth(request)
        
    data = request.POST
    
    
    html = data.get('quill_html')
    quill = data.get('quill_delta')
    subject = data.get('email_subject')
    target_recipients = data.get('email_target_recipients')
    organisation = None
    opportunity = None
    
    if target_recipients == 'all_org_volunteers':
        organisation = data.get('org_id')
        organisation = Organisation.objects.get(id=organisation)

    if target_recipients == 'all_opp_volunteers':
        opportunity = data.get('opp_id')
        opportunity = Opportunity.objects.get(id=opportunity)
    
    
    if data.get('email_id') != 'None':
        draft = EmailDraft.objects.get(id=data.get('email_id'))
        draft.subject = subject
        draft.email_quill = quill
        draft.email_html = html
        draft.last_modified = datetime.now()
        draft.save()
        
        if target_recipients == 'all_org_volunteers':
            draft.organisation = organisation
            draft.opportunity = None
            
        if target_recipients == 'all_opp_volunteers':
            draft.opportunity = opportunity
            draft.organisation = None
            
        draft.email_target_recipients = target_recipients
        
        draft.save()
        return redirect('edit_email_draft', draft.id)
    
    if target_recipients == 'all_org_volunteers':
        draft = EmailDraft.objects.create(
            subject=subject,
            email_quill=quill,
            email_html=html,
            email_target_recipients = target_recipients,
            organisation = organisation,
            sent=False,
            sent_by=request.user
        )
        
        draft.save()
        
        return redirect('edit_email_draft', draft.id)
    
    if target_recipients == 'all_opp_volunteers':
        draft = EmailDraft.objects.create(
            subject=subject,
            email_quill=quill,
            email_html=html,
            email_target_recipients = target_recipients,
            opportunity = opportunity,
            sent=False,
            sent_by=request.user
        )
        
        draft.save()
        
        return redirect('edit_email_draft', draft.id)

    draft = EmailDraft.objects.create(
        subject=subject,
        email_quill=quill,
        email_html=html,
        email_target_recipients = target_recipients,
        sent=False,
        sent_by=request.user
    )
    
    draft.save()
    
    return redirect('edit_email_draft', draft.id)
    

def edit_email_draft(request, draft_id=None):
    check_auth(request)
    
    if draft_id:
        draft = EmailDraft.objects.get(id=draft_id)
    else:
        draft = None
    
    context = {
        'orgs': Organisation.objects.all(),
        'opps': Opportunity.objects.all(),
        'editor_id': "".join(random.choices(string.ascii_letters, k=10)),
        'draft_id': draft_id,
        'subject': draft.subject if draft else '',
        'draft': draft,
        'email_quill': draft.email_quill if draft else '',
        'hx': check_if_hx(request)
    }
    
    return render(request, 'org_admin/email_portal/email_editor.html', context)

def delete_email_draft(request, draft_id):
    check_auth(request)
    
    EmailDraft.objects.get(id=draft_id).delete()
    
    return redirect('email_portal_index')

def send_email_draft(request, draft_id, confirm_id=None):
    check_auth(request)
    
    draft = EmailDraft.objects.get(id=draft_id)
    
    if draft.email_target_recipients == 'volunteers':
        recipients = Volunteer.objects.all()
    elif draft.email_target_recipients == 'admins':
        recipients = OrganisationAdmin.objects.all()
    elif draft.email_target_recipients == 'all_org_volunteers':
        regs = Registration.objects.filter(opportunity__organisation=draft.organisation)
        recipients = [reg.volunteer for reg in regs if reg.get_registration_status() not in ['stopped', 'completed']]
    elif draft.email_target_recipients == 'all_opp_volunteers':
        regs = Registration.objects.filter(opportunity=draft.opportunity)
        recipients = [reg.volunteer for reg in regs if reg.get_registration_status() not in ['stopped', 'completed']]
    else:
        recipients = None
        
    print (recipients)
    
    if confirm_id and recipients:
        
        if confirm_id != draft.send_confirmation_id:
            return email_portal_index(request, error="Invalid confirmation ID")
        
        if draft.sent:
            return email_portal_index(request, error="Email has already been sent")
        
        connection = get_connection()
        connection.open()
        
        for recipient in recipients:
            threading.Thread(target=send_email, args=(draft, recipient)).start()
        
        connection.close()
        
        draft.sent = True
        draft.sent_date = datetime.now()
        draft.sent_by = request.user
        draft.save()
        
        return email_portal_index(request, success="Email sent successfully")
        
    draft.send_confirmation_id = "".join(random.choices(string.ascii_letters, k=10))
    draft.save()
    
    draft_render_context = {
        'name': request.user.first_name + " " + request.user.last_name,
        'content': draft.email_html
    }
    
    draft_render = render_to_string('org_admin/email_portal/email_template.html', draft_render_context)
    
    context = {
        'hx': check_if_hx(request),
        'recipients': recipients,
        'draft': draft,
        'draft_render': draft_render,
    }
    
    return render(request, 'org_admin/email_portal/confirm_send.html', context)

def preview_email(request, draft_id):
    check_auth(request)
    
    context = {
        'html': EmailDraft.objects.get(id=draft_id).email_html,
        'draft_id': draft_id,
        'subject': EmailDraft.objects.get(id=draft_id).subject,
        'hx': check_if_hx(request)
    }
    
    return render(request, 'org_admin/email_portal/email_preview.html', context)

def view_email_detail(request, draft_id):
    check_auth(request)
    
    context = {
        'draft': EmailDraft.objects.get(id=draft_id),
        'hx': check_if_hx(request)
    }
    
    return render(request, 'org_admin/email_portal/view_email_detail.html', context)

def duplicate_email_draft(request, draft_id):
    check_auth(request)
    
    draft = EmailDraft.objects.get(id=draft_id)
    
    new_draft = EmailDraft.objects.create(
        subject=draft.subject,
        email_quill=draft.email_quill,
        email_html=draft.email_html,
        email_target_recipients=draft.email_target_recipients,
        organisation = draft.organisation,
        opportunity = draft.opportunity,
        sent=False,
        sent_by=request.user
    )
    
    new_draft.save()
    
    return redirect('email_portal_index')

def send_email(draft, recipient):
    subject = draft.subject
    html = draft.email_html
    
    context = {
        'name': recipient.user.first_name + " " + recipient.user.last_name,
        'content': draft.email_html
    }
    
    text = render_to_string('org_admin/email_portal/email_template.html', context)
 
    
    email = EmailMultiAlternatives(
        subject=subject,
        body=text,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[recipient.user.email]
    )
    
    email.attach_alternative(text, "text/html")
    email.send()
    
    #if seding is successful, add the recipient to the draft
    draft.email_recipients.add(recipient.user)
    draft.save()
    
    return True