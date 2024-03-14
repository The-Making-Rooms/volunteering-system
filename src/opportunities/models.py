from django.db import models
from djrichtextfield.models import RichTextField
from recurrence.fields import RecurrenceField
from django.conf import settings

# Create your models here.
class Opportunity(models.Model):
    name = models.CharField(max_length=200)
    description = RichTextField()
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    recurrences = RecurrenceField(null=True)
    organisation = models.ForeignKey('organisations.organisation', on_delete=models.CASCADE)
    featured = models.BooleanField(default=False)
class Benefit(models.Model):
    description = models.CharField(max_length=200)
    opportunity = models.ForeignKey('Opportunity', on_delete=models.CASCADE)

class Location(models.Model):
    opportunity = models.ForeignKey('Opportunity', on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    description = RichTextField()
    first_line = models.CharField(max_length=200)
    second_line = models.CharField(max_length=200)
    postcode = models.CharField(max_length=200)
    city = models.CharField(max_length=200)
    longitude = models.FloatField()
    latitude = models.FloatField()

class Registration(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    opportunity = models.ForeignKey('Opportunity', on_delete=models.CASCADE)

class Image(models.Model):
    image = models.ImageField(upload_to='images/')
    opportunity = models.ForeignKey('Opportunity', on_delete=models.CASCADE)

class Video(models.Model):
    video = models.FileField(upload_to='videos/')
    opportunity = models.ForeignKey('Opportunity', on_delete=models.CASCADE)

class LinkedTags(models.Model):
    opportunity = models.ForeignKey('Opportunity', on_delete=models.CASCADE)
    tag = models.ForeignKey('Tag', on_delete=models.CASCADE)

class Tag(models.Model):
    tag = models.CharField(max_length=100)

class SupplimentaryInfoRequirement(models.Model):
    opportunity = models.ForeignKey('Opportunity', on_delete=models.CASCADE)
    info = models.ForeignKey('volunteer.SupplementaryInfo', on_delete=models.CASCADE)

