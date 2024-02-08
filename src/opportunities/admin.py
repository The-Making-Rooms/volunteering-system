from django.contrib import admin
from opportunities.models import Benefit, Location, Opportunity, Image, Video, SupplimentaryInfoRequirement

# Register your models here.
class BenefitInline(admin.TabularInline):
    model = Benefit
    extra = 1

class LocationInline(admin.TabularInline):
    model = Location
    extra = 1

class ImageInline(admin.TabularInline):
    model = Image
    extra = 1

class VideoInline(admin.TabularInline):
    model = Video
    extra = 1


@admin.register(Opportunity)
class OpportunityAdmin(admin.ModelAdmin):
    list_display = ('name', 'organisation')
    search_fields = ('name', 'organisation')
    inlines = [BenefitInline, LocationInline, ImageInline, VideoInline]

@admin.register(SupplimentaryInfoRequirement)
class SupplimentaryInfoRequirementAdmin(admin.ModelAdmin):
    list_display = ('opportunity', 'info')