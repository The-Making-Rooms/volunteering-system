from typing import Any
from django.contrib import admin
from organisations.models import Link, Organisation, Image, Video, thematicCategory, organisationnThematicLink, Location, LinkType
from org_admin.models import OrganisationAdmin
# Register your models here.

class LinkInline(admin.TabularInline):
    model = Link
    extra = 1

class AddressInline(admin.TabularInline):
    model = Location
    extra = 1

class ImageInline(admin.TabularInline):
    model = Image
    extra = 1

class VideoInline(admin.TabularInline):
    model = Video
    extra = 1

class ThematicInLine(admin.TabularInline):
    model = organisationnThematicLink
    extra = 1

@admin.register(Organisation)
class OrganisationAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']
    inlines = [LinkInline, ImageInline, VideoInline, AddressInline, ThematicInLine]
    
    #only show organisations where user is the owner
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        admin_orgs = OrganisationAdmin.objects.filter(user=request.user)
        return qs.filter(id__in=[org.organisation.id for org in admin_orgs])

@admin.register(thematicCategory)
class ThematicAdmin(admin.ModelAdmin):
    pass

@admin.register(LinkType)
class LinkTypeAdmin(admin.ModelAdmin):
    list_display = ['name']