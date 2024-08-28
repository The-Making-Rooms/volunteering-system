from django.contrib import admin
from opportunities.models import Benefit, Location, Opportunity, Image, Video, SupplimentaryInfoRequirement, Registration, RegistrationStatus, VolunteerRegistrationStatus, LinkedTags, Tag, Icon, OpportunityBenefit

# Register your models here.
class BenefitInline(admin.TabularInline):
    model = Benefit
    extra = 1

class LinkedTagsInline(admin.TabularInline):
    model = LinkedTags
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

@admin.register(RegistrationStatus)
class RegistrationStatusAdmin(admin.ModelAdmin):
    pass

@admin.register(VolunteerRegistrationStatus)
class VolunteerRegistrationStatusAdmin(admin.ModelAdmin):
    pass

@admin.register(Opportunity)
class OpportunityAdmin(admin.ModelAdmin):
    list_display = ('name', 'organisation')
    search_fields = ('name', 'organisation')
    inlines = [BenefitInline, LocationInline, ImageInline, VideoInline, LinkedTagsInline]

@admin.register(SupplimentaryInfoRequirement)
class SupplimentaryInfoRequirementAdmin(admin.ModelAdmin):
    list_display = ('opportunity', 'info')

@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = ('volunteer', 'opportunity', 'get_registration_status')
    pass

@admin.register(Tag)
class TagsAdmin(admin.ModelAdmin):
    pass

@admin.register(Icon)
class IconAdmin(admin.ModelAdmin):
    pass

@admin.register(OpportunityBenefit)
class OpportunityBenefitAdmin(admin.ModelAdmin):
    pass