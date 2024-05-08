from django.db import models
from djrichtextfield.models import RichTextField
from recurrence.fields import RecurrenceField
from django.conf import settings

# Create your models here.
class Opportunity(models.Model):
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=500)
    recurrences = RecurrenceField(null=True)
    start_time = models.TimeField()
    end_time = models.TimeField()
    organisation = models.ForeignKey('organisations.organisation', on_delete=models.CASCADE)
    active = models.BooleanField(default=False)
    featured = models.BooleanField(default=False)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Opportunities"

class OpportunityView(models.Model):
    opportunity = models.ForeignKey('Opportunity', on_delete=models.CASCADE)
    time = models.DateTimeField(auto_now_add=True)

class Benefit(models.Model):
    description = models.CharField(max_length=200)
    opportunity = models.ForeignKey('Opportunity', on_delete=models.CASCADE)

class Location(models.Model):
    opportunity = models.ForeignKey('Opportunity', on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    address = RichTextField(null=True, blank=True)
    place_id = models.CharField(blank=True, null=True,max_length=200)
    longitude = models.FloatField(null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)

class RegistrationStatus(models.Model):
    status = models.CharField(max_length=200)
    
    class Meta:
        verbose_name_plural = "Registration Statuses"
    
class VolunteerRegistrationStatus(models.Model):
    registration = models.ForeignKey('Registration', on_delete=models.CASCADE)
    registration_status = models.ForeignKey('RegistrationStatus', on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.registration.volunteer.user.username
    
    def get_status(self):
        return self.registration_status.status
    
    def get_organisation(self):
        return self.registration.opportunity.organisation.name
    
    class Meta:
        verbose_name_plural = "Volunteer Registration Statuses"
    
class Registration(models.Model):
    volunteer = models.ForeignKey('volunteer.Volunteer', on_delete=models.CASCADE)
    opportunity = models.ForeignKey('Opportunity', on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True)
    
    def get_registration_status(self):
        return VolunteerRegistrationStatus.objects.filter(registration=self).last().registration_status.status

class RegistrationAbsence(models.Model):
    registration = models.ForeignKey('Registration', on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)

class Image(models.Model):
    image = models.ImageField(upload_to='images/')
    thumbnail_image = models.ImageField(upload_to='images/', null=True, blank=True)
    opportunity = models.ForeignKey('Opportunity', on_delete=models.CASCADE)

class Video(models.Model):
    video = models.FileField(upload_to='videos/')
    video_thumbnail = models.ImageField(upload_to='videos/', null=True, blank=True)
    opportunity = models.ForeignKey('Opportunity', on_delete=models.CASCADE)

class LinkedTags(models.Model):
    opportunity = models.ForeignKey('Opportunity', on_delete=models.CASCADE)
    tag = models.OneToOneField('Tag', on_delete=models.CASCADE)

class Tag(models.Model):
    tag = models.CharField(max_length=100, unique=True)

class SupplimentaryInfoRequirement(models.Model):
    opportunity = models.ForeignKey('Opportunity', on_delete=models.CASCADE)
    info = models.ForeignKey('volunteer.SupplementaryInfo', on_delete=models.CASCADE)

