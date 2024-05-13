from django.db import models
from djrichtextfield.models import RichTextField
from recurrence.fields import RecurrenceField
from django.conf import settings
import random
import requests
from io import BytesIO
from django.core.files.base import ContentFile

def generate_random_pastel_hex():
    red = random.randint(0, 255)
    green = random.randint(0, 255)
    blue = random.randint(0, 255)
    
    red = (red + 255) // 2
    green = (green + 255) // 2
    blue = (blue + 255) // 2
    
    print(red, green, blue)
    
    return "#{:02x}{:02x}{:02x}".format(red, green, blue)
    

def generate_darker_gradient_hex(colour):
    #more lighter
    red = int(colour[1:3], 16)
    green = int(colour[3:5], 16)
    blue = int(colour[5:7], 16)
    
    red = (red + 255) // 2
    green = (green + 255) // 2
    blue = (blue + 255) // 2
    
    return "#{:02x}{:02x}{:02x}".format(red, green, blue)

def get_default_icon():
    if Icon.objects.filter(name="Default").exists():
        return Icon.objects.get(name="Default")
    else:
        url = "https://static.thenounproject.com/png/2030120-200.png"

        img_bytes = requests.get(url).content
        bytes_io = BytesIO(img_bytes)

        icon = Icon.objects.create(name="Default")
        icon.icon.save("default_icon.png", ContentFile(bytes_io.getvalue()))
        icon.save()
        
        return icon
   
        
        
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

class Icon(models.Model):
    icon = models.ImageField(upload_to='icons/')
    name = models.CharField(max_length=200)
    tags = models.CharField(max_length=200, null=True, blank=True)
    invert = models.BooleanField(default=False)

class Benefit(models.Model):
    icon = models.ForeignKey('Icon', default=get_default_icon, on_delete=models.CASCADE)
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
        
    def __str__(self):
        return self.status
    
class VolunteerRegistrationStatus(models.Model):
    registration = models.ForeignKey('Registration', on_delete=models.CASCADE)
    registration_status = models.ForeignKey('RegistrationStatus', on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True, editable=True)
    
    def __str__(self):
        return self.registration.volunteer.user.username + " - " + self.registration.opportunity.name + " - " + self.registration_status.status
    
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
    tag = models.ForeignKey('Tag', on_delete=models.CASCADE)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['opportunity', 'tag'], name='unique_opportunity_tag')
        ]

class Tag(models.Model):
    tag = models.CharField(max_length=100, unique=True)
    hex_colour = models.CharField(max_length=7)
    hex_colour_to = models.CharField(max_length=7)
    
    def save(self, *args, **kwargs):
        if not self.hex_colour:
            self.hex_colour = generate_random_pastel_hex()
        if not self.hex_colour_to:
            self.hex_colour_to = generate_darker_gradient_hex(self.hex_colour)
        super().save(*args, **kwargs)
    

class SupplimentaryInfoRequirement(models.Model):
    opportunity = models.ForeignKey('Opportunity', on_delete=models.CASCADE)
    info = models.ForeignKey('volunteer.SupplementaryInfo', on_delete=models.CASCADE)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['opportunity', 'info'], name='unique_opportunity_info')
        ]

