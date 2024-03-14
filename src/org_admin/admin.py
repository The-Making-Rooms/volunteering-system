from django.contrib import admin
from .models import OrgnaisationAdmin
# Register your models here.

@admin.register(OrgnaisationAdmin)
class OrgnaisationAdminAdmin(admin.ModelAdmin):
    list_display = ('user', 'organisation')
    search_fields = ('user', 'organisation')
    pass