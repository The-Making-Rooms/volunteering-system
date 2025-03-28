from celery import shared_task
from .models import OrganisationAdmin
from django.core.mail import EmailMultiAlternatives, get_connection
from django.conf import settings
from django.template.loader import render_to_string
import os


@shared_task
def add(x, y):
    return x + y

@shared_task
def send_reminder_email_org_admins():
    admins = OrganisationAdmin.objects.all()
    
    connection = get_connection(
        username=os.environ.get('EMAIL_HOST_USER'),
        password=os.environ.get('EMAIL_HOST_PASSWORD'),
        fail_silently=False
    )
    
    connection.open()
    
    for admin in admins:
        rendered_email = render_to_string('org_admin/automated_emails/login_reminder.html', {'org_name': admin.organisation.name})
        
        email = EmailMultiAlternatives(
            subject='Chip In: Log in reminder',
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[admin.user.email],
            
        )
        
        email.attach_alternative(rendered_email, 'text/html')
        email.send()
        
    connection.close()    
    return True
    
            