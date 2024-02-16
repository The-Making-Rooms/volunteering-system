from django.db import models
from djrichtextfield.models import RichTextField

# Create your models here.
class Organisation(models.Model):
    name = models.CharField(max_length=200)
    description = RichTextField()
    featured = models.BooleanField(default=False)

class Location(models.Model):
    name = models.CharField(max_length=200)
    description = RichTextField(null=True, blank=True)
    first_line = models.CharField(max_length=200)
    second_line = models.CharField(max_length=200, null=True, blank=True)
    postcode = models.CharField(max_length=200)
    city = models.CharField(max_length=200)
    organisation = models.ForeignKey('Organisation', on_delete=models.CASCADE)
    longitude = models.FloatField(null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)

class Link(models.Model):
    name = models.CharField(max_length=200)
    link = models.CharField(max_length=200)
    icon = models.ImageField(null=True, blank=True)
    description = models.CharField(max_length=200, null=True, blank=True)
    organisation = models.ForeignKey('Organisation', on_delete=models.CASCADE)

class Image(models.Model):
    image = models.ImageField(upload_to='images/')
    organisation = models.ForeignKey('Organisation', on_delete=models.CASCADE)

class Video(models.Model):
    video = models.FileField(upload_to='videos/')
    organisation = models.ForeignKey('Organisation', on_delete=models.CASCADE)

class thematicCategory(models.Model):
    hex_colour = models.CharField(max_length = 7)
    name = models.CharField(max_length = 100)
    image = models.ImageField(upload_to='thematic/')

class organisationnThematicLink(models.Model):
    organisation = models.ForeignKey('Organisation', on_delete=models.CASCADE)
    theme = models.ForeignKey('thematicCategory', on_delete=models.CASCADE)


