from django.db import models
from djrichtextfield.models import RichTextField
from org_admin.models import OrgnaisationAdmin

# Create your models here.
class Organisation(models.Model):
    name = models.CharField(max_length=200)
    logo = models.ImageField(upload_to='logos/', null=True, blank=True)
    description = RichTextField()
    featured = models.BooleanField(default=False)

    def get_orgnanisation_admin_users(self):
        return OrgnaisationAdmin.objects.filter(organisation=self).values_list('user', flat=True)
    
    def __str__(self):
        return self.name

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

class LinkType(models.Model):
    icon = models.ImageField(null=True, blank=True)
    name = models.CharField(max_length=200)

class Link(models.Model):
    link_type = models.ForeignKey('LinkType', on_delete=models.CASCADE, blank=True, null=True)
    name = models.CharField(max_length=200)
    url = models.CharField(max_length=200)
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


