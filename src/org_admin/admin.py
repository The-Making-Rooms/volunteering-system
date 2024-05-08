from django.contrib import admin
from .models import OrganisationAdmin
# Register your models here.

@admin.register(OrganisationAdmin)
class OrganisationAdminAdmin(admin.ModelAdmin):
    list_display = ('user', 'organisation')
    search_fields = ('user', 'organisation')
    pass