"""
VolunteeringSystem

This project is distributed under the CC BY-NC-SA 4.0 license. See LICENSE for details.
"""

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
    
    filled_by_organisation = models.BooleanField(default=False)
    visible_to_all = models.BooleanField(default=False)        
    
    def __str__(self):
        return self.name
    
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