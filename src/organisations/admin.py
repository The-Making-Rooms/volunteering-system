from typing import Any
from django.contrib import admin
from organisations.models import Link, Organisation, Image, Video
# Register your models here.

class LinkInline(admin.TabularInline):
    model = Link
    extra = 1

class ImageInline(admin.TabularInline):
    model = Image
    extra = 1

class VideoInline(admin.TabularInline):
    model = Video
    extra = 1
    
@admin.register(Organisation)
class OrganisationAdmin(admin.ModelAdmin):
    list_display = ('name', 'location')
    search_fields = ('name', 'location')
    inlines = [LinkInline, ImageInline, VideoInline]




