"""
VolunteeringSystem

This project is distributed under the CC BY-NC-SA 4.0 license. See LICENSE for details.
"""

from django.contrib import admin
from volunteer.models import Volunteer, VolunteerAddress, VolunteerConditions, VolunteerInterest, EmergencyContacts, SupplementaryInfo, SupplementaryInfoGrantee, VolunteerSupplementaryInfo, MentorRecord, MentorSession, MentorNotes
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
    
class MentorSessionInLine(admin.TabularInline):
    model = MentorSession
    extra = 1

class MentorNotesInLine(admin.TabularInline):
    model = MentorNotes
    extra = 1
    
@admin.register(MentorRecord)
class MentorRecordAdmin(admin.ModelAdmin):
    inlines = [MentorSessionInLine, MentorNotesInLine]

@admin.register(Volunteer)
class VolunteerAdmin(admin.ModelAdmin):
    inlines = [VolunteerAddressInline, VolunteerConditionsInline, VolunteerInterestInline, EmergencyContactInline]

@admin.register(SupplementaryInfo)
class SupplementaryInfoAdmin(admin.ModelAdmin):
    list_display = ('title', 'description')
    
    pass

@admin.register(SupplementaryInfoGrantee)
class SupplementaryInfoGranteeAdmin(admin.ModelAdmin):
    list_display = ('org', 'info')


@admin.register(VolunteerSupplementaryInfo)
class VolunteerSupplementaryInfoAdmin(admin.ModelAdmin):
    list_display = ('volunteer', 'info', 'last_updated')
    pass