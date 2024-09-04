from django.db import models
from org_admin.models import OrganisationAdmin
from PIL import Image as PImage
import uuid
import os

def get_random_filename_image(instance, filename):
    ext = filename.split('.')[-1]
    random_filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join('images/', random_filename)

def get_random_filename_video(instance, filename):
    ext = filename.split('.')[-1]
    random_filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join('videos/', random_filename)


class Organisation(models.Model):
    name = models.CharField(max_length=200)
    logo = models.ImageField(upload_to='logos/', null=True, blank=True)
    description = models.TextField()
    featured = models.BooleanField(default=False)

    def get_orgnanisation_admin_users(self):
        return OrganisationAdmin.objects.filter(organisation=self).values_list('user', flat=True)
    
    def __str__(self):
        return self.name

class Location(models.Model):
    name = models.CharField(max_length=200)
    address = models.CharField(max_length=200, blank=True, null=True)
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
    image = models.ImageField(upload_to=get_random_filename_image)
    organisation = models.ForeignKey('Organisation', on_delete=models.CASCADE)
    thumbnail_image = models.ImageField(upload_to=get_random_filename_image, null=True, blank=True)
    
class Badge(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to='badges/')
    organisation = models.ForeignKey('Organisation', on_delete=models.CASCADE, null=True, blank=True)
    
class BadgeOpporunity(models.Model):
    opportunity = models.ForeignKey('opportunities.Opportunity', on_delete=models.CASCADE)
    badge = models.ForeignKey('Badge', on_delete=models.CASCADE)
    
    class Meta:
        unique_together = ('opportunity', 'badge')
        
class VolunteerBadge(models.Model):
    badge = models.ForeignKey('Badge', on_delete=models.CASCADE)
    volunteer = models.ForeignKey('volunteer.Volunteer', on_delete=models.CASCADE)
    date_awarded = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('badge', 'volunteer')


class Video(models.Model):
    video = models.FileField(upload_to=get_random_filename_video)
    video_thumbnail = models.ImageField(upload_to=get_random_filename_video, null=True, blank=True)
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
    
class OrganisationInterest(models.Model):
    volunteer = models.ForeignKey('volunteer.Volunteer', on_delete=models.CASCADE)
    organisation = models.ForeignKey('Organisation', on_delete=models.CASCADE)
    date_interest = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('volunteer', 'organisation')

