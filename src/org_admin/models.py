"""
VolunteeringSystem

This project is distributed under the CC BY-NC-SA 4.0 license. See LICENSE for details.
"""

from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

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
        ('all_org_volunteers', 'All organisation volunteers'),
        ('all_opp_volunteers', 'All opportunity volunteers'),
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
    
    opportunity = models.ForeignKey('opportunities.Opportunity', on_delete=models.CASCADE, null=True)
    organisation = models.ForeignKey('organisations.Organisation', on_delete=models.CASCADE, null=True)
    
    created_date = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    
    #check if a valid organisation is selected or opportuinty if target is all_org_volunteers or all_opp_volunteers
    def clean(self):
        if self.email_target_recipients == 'all_org_volunteers':
            if self.organisation is None:
                raise ValidationError('Organisation must be selected')
        if self.email_target_recipients == 'all_opp_volunteers':
            if self.opportunity is None:
                raise ValidationError('Opportunity must be selected')