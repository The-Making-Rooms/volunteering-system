from django.contrib import admin
from .models import Form, Question, Options, Answer, Response
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
