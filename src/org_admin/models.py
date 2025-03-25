"""
VolunteeringSystem

This project is distributed under the CC BY-NC-SA 4.0 license. See LICENSE for details.
"""

from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
# Create your models here.
class OrganisationAdmin(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    organisation = models.ForeignKey('organisations.Organisation', on_delete=models.CASCADE)
    
class NotificationPreference(models.Model):
    email_on_message = models.BooleanField(default=True)
    email_on_registration = models.BooleanField(default=True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

class EmailDraft(models.Model):
    
    RECIPIENT_CHOICES = {
        ('all', 'All users'),
        ('volunteers', 'Volunteers'),
        ('organisations', 'Organisations'),
    }
    
    subject = models.CharField(max_length=100)
    
    email_quill = models.TextField()
    email_html = models.TextField()
    
    send_confirmation_id = models.CharField(max_length=20, null=True)
    
    email_target_recipients = models.CharField(max_length=20, choices=RECIPIENT_CHOICES)
    email_recipients = models.ManyToManyField(settings.AUTH_USER_MODEL)
    
    sent = models.BooleanField(default=False)
    sent_date = models.DateTimeField(null=True)
    sent_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_by')
    
    created_date = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)