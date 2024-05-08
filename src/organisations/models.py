from django.db import models
from djrichtextfield.models import RichTextField
from org_admin.models import OrganisationAdmin
from PIL import Image as PImage
import uuid
import os

# Create your models here.
class Organisation(models.Model):
    name = models.CharField(max_length=200)
    logo = models.ImageField(upload_to='logos/', null=True, blank=True)
    description = RichTextField()
    featured = models.BooleanField(default=False)

    def get_orgnanisation_admin_users(self):
        return OrganisationAdmin.objects.filter(organisation=self).values_list('user', flat=True)
    
    def __str__(self):
        return self.name

class Location(models.Model):
    name = models.CharField(max_length=200)
    address = RichTextField(null=True, blank=True)
    place_id = models.CharField(blank=True, null=True,max_length=200)
    organisation = models.ForeignKey('Organisation', on_delete=models.CASCADE)
    longitude = models.FloatField(null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)


class LinkType(models.Model):
    icon = models.FileField(null=True, blank=True)
    name = models.CharField(max_length=200)
    
    def __str__(self):
        return self.name

class Link(models.Model):
    link_type = models.ForeignKey('LinkType', on_delete=models.CASCADE, blank=True, null=True)
    url = models.CharField(max_length=200)
    organisation = models.ForeignKey('Organisation', on_delete=models.CASCADE)
    clicks = models.IntegerField(default=0)

class Image(models.Model):
    image = models.ImageField(upload_to='images/')
    organisation = models.ForeignKey('Organisation', on_delete=models.CASCADE)
    thumbnail_image = models.ImageField(upload_to='images/', null=True, blank=True)
    


class Video(models.Model):
    video = models.FileField(upload_to='videos/')
    video_thumbnail = models.ImageField(upload_to='videos/', null=True, blank=True)
    organisation = models.ForeignKey('Organisation', on_delete=models.CASCADE)

class thematicCategory(models.Model):
    hex_colour = models.CharField(max_length = 7)
    name = models.CharField(max_length = 100)
    image = models.ImageField(upload_to='thematic/')
    
    class Meta:
        verbose_name_plural = "Thematic Categories"

class organisationnThematicLink(models.Model):
    organisation = models.ForeignKey('Organisation', on_delete=models.CASCADE)
    theme = models.ForeignKey('thematicCategory', on_delete=models.CASCADE)


