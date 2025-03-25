"""
VolunteeringSystem

This project is distributed under the CC BY-NC-SA 4.0 license. See LICENSE for details.
"""

from django.contrib import admin
from .models import OrganisationAdmin, NotificationPreference, EmailDraft
# Register your models here.


@admin.register(OrganisationAdmin)
class OrganisationAdminAdmin(admin.ModelAdmin):
    list_display = ('user', 'organisation')
    search_fields = ('user', 'organisation')
    
@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = ('user','email_on_message', 'email_on_registration')
    search_fields = ('user''email_on_message', 'email_on_registration')

@admin.register(EmailDraft)
class EmailDraftAdmin(admin.ModelAdmin):
    list_display = ('subject', 'sent', 'sent_by')
    search_fields = ('subject', 'sent', 'sent_by')
    readonly_fields = ('sent_by', 'last_modified')