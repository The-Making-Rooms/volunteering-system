"""
VolunteeringSystem

This project is distributed under the CC BY-NC-SA 4.0 license. See LICENSE for details.
"""

import uuid
from django.db import models

# Create your models here.
class Form(models.Model):
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=500)
    allow_multiple = models.BooleanField(default=False)
    organisation = models.ForeignKey('organisations.Organisation', on_delete=models.CASCADE, null=True, blank=True)
    
    required_on_signup = models.BooleanField(default=False)
    
    mentor_start_form = models.BooleanField(default=False)
    mentor_end_form = models.BooleanField(default=False)
    sign_up_form = models.BooleanField(default=False)
    
    filled_by_organisation = models.BooleanField(default=False)
    visible_to_all = models.BooleanField(default=False)        
    
    def __str__(self):
        return self.name
    
    #enforce only one for for mentor start and end and sign up
    def save(self, *args, **kwargs):
        if Form.objects.filter(mentor_start_form=True).count() > 1:
            raise Exception("Only one form can be the mentor start form")
        if Form.objects.filter(mentor_end_form=True).count() > 1:
            raise Exception("Only one form can be the mentor end form")
        if Form.objects.filter(sign_up_form=True).count() > 1:
            raise Exception("Only one form can be the sign up form")
        super(Form, self).save(*args, **kwargs)
    
class Question(models.Model):
    form = models.ForeignKey('Form', on_delete=models.CASCADE)
    index = models.IntegerField()
    question = models.CharField(max_length=1000)
    question_type = models.CharField(max_length=200)
    required = models.BooleanField(default=False)
    allow_multiple = models.BooleanField(default=False)
    def __str__(self):
        return self.question
    
class Options(models.Model):
    question = models.ForeignKey('Question', on_delete=models.CASCADE)
    option = models.CharField(max_length=200)
    
    def __str__(self):
        return self.option
    
class Response(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    form = models.ForeignKey('Form', on_delete=models.CASCADE)
    response_date = models.DateTimeField(auto_now_add=True)
    
class Answer(models.Model):
    question = models.ForeignKey('Question', on_delete=models.CASCADE)
    answer = models.CharField(max_length=200, null=True, blank=True)
    response = models.ForeignKey('Response', on_delete=models.CASCADE, blank=True, null=True)
    
    def __str__(self):
        return str(self.answer)

class FormResponseRequirement(models.Model):
    form = models.ForeignKey('Form', on_delete=models.CASCADE)
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
    assigned = models.DateTimeField(auto_now_add=True)

class OrganisationFormResponseRequirement(models.Model):
    form = models.ForeignKey('Form', on_delete=models.CASCADE)
    organisation = models.ForeignKey('organisations.Organisation', on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
    assigned = models.DateTimeField(auto_now_add=True)

class SuperForm(models.Model):
    #override id to use UUID
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    active = models.BooleanField(default=True)
    
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=500)
    photo = models.ImageField(upload_to='superforms/', blank=True, null=True)
    submitted_message = models.TextField(blank=True, null=True)
    
    background_colour = models.CharField(max_length=7, default="#FFFFFF")
    card_background_colour = models.CharField(max_length=7, default="#FFFFFF")
    card_text_colour = models.CharField(max_length=7, default="#000000")
    
    show_form_titles = models.BooleanField(default=True)
    show_form_descriptions = models.BooleanField(default=True)
    
    forms_to_complete = models.ManyToManyField('Form', blank=True)
    opportunity_to_register = models.ForeignKey('opportunities.Opportunity', on_delete=models.CASCADE, blank=True, null=True)
    
class SuperFormRegistration(models.Model):
    """Model to keep track of superform registrations"""
    
    #override id to use UUID
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    submitted = models.DateTimeField(auto_now_add=True)
    superform = models.ForeignKey('SuperForm', on_delete=models.CASCADE)