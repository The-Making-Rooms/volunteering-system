from django.db import models
from djrichtextfield.models import RichTextField

# Create your models here.
class Organisation(models.Model):
    name = models.CharField(max_length=200)
    description = RichTextField()
    location = models.CharField(max_length=200)

class Link(models.Model):
    name = models.CharField(max_length=200)
    link = models.CharField(max_length=200)
    icon = models.ImageField()
    description = models.CharField(max_length=200)
    organisation = models.ForeignKey('Organisation', on_delete=models.CASCADE)

class Image(models.Model):
    image = models.ImageField(upload_to='images/')
    organisation = models.ForeignKey('Organisation', on_delete=models.CASCADE)

class Video(models.Model):
    video = models.FileField(upload_to='videos/')
    organisation = models.ForeignKey('Organisation', on_delete=models.CASCADE)