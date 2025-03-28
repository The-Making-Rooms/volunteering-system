"""
VolunteeringSystem

This project is distributed under the CC BY-NC-SA 4.0 license. See LICENSE for details.
"""

from django.contrib import admin
from .models import Form, Question, Options, Answer, Response, FormResponseRequirement, OrganisationFormResponseRequirement
# Register your models here.


#register question to inlines for form

class OptionsInline(admin.TabularInline):
    model = Options
    extra = 1
    
class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1
    inlines = [OptionsInline]
    
class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 1
    
@admin.register(Form)
class FormAdmin(admin.ModelAdmin):
    inlines = [QuestionInline]
    
@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    inlines = [OptionsInline]
    
@admin.register(Options)
class OptionsAdmin(admin.ModelAdmin):
    pass

@admin.register(Response)
class ResponseAdmin(admin.ModelAdmin):
    inlines = [AnswerInline]

@admin.register(FormResponseRequirement)
class FormResponseRequirementAdmin(admin.ModelAdmin):
    pass

@admin.register(OrganisationFormResponseRequirement)
class OrganisationFormResponseRequirementAdmin(admin.ModelAdmin):
    pass