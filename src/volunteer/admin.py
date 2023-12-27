from django.contrib import admin
from volunteer.models import Volunteer, VolunteerAddress, VolunteerConditions, VolunteerInterest, EmergencyContacts
# Register your models here.
class VolunteerAddressInline(admin.TabularInline):
    model = VolunteerAddress
    extra = 1

class VolunteerConditionsInline(admin.TabularInline):
    model = VolunteerConditions
    extra = 1

class VolunteerInterestInline(admin.TabularInline):
    model = VolunteerInterest
    extra = 1

class EmergencyContactInline(admin.TabularInline):
    model = EmergencyContacts
    extra = 1

@admin.register(Volunteer)
class OpportunityAdmin(admin.ModelAdmin):
    inlines = [VolunteerAddressInline, VolunteerConditionsInline, VolunteerInterestInline, EmergencyContactInline]
