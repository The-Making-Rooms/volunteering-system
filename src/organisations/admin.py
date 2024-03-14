from typing import Any
from django.contrib import admin
from organisations.models import Link, Organisation, Image, Video, thematicCategory, organisationnThematicLink, Location
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

@admin.register(thematicCategory)
class ThematicAdmin(admin.ModelAdmin):
    pass