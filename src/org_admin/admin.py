"""
VolunteeringSystem

This project is distributed under the CC BY-NC-SA 4.0 license. See LICENSE for details.
"""

from django.contrib import admin
from .models import OrganisationAdmin
# Register your models here.

@admin.register(OrganisationAdmin)
class OrganisationAdminAdmin(admin.ModelAdmin):
    list_display = ('user', 'organisation')
    search_fields = ('user', 'organisation')
    pass