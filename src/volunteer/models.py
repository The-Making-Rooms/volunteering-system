from django.db import models
from django.conf import settings

# Create your models here.
class Volunteer(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatars/')
    date_of_birth = models.DateField()
    phone_number = models.CharField(max_length=11)
    bio = models.TextField()
    CV = models.FileField(upload_to='CV/')

class VolunteerAddress(models.Model):
    first_line = models.CharField(max_length=200)
    second_line = models.CharField(max_length=200)
    postcode = models.CharField(max_length=200)
    city = models.CharField(max_length=200)
    volunteer = models.ForeignKey('Volunteer', on_delete=models.CASCADE)

class EmergencyContacts(models.Model):
    name = models.CharField(max_length=200)
    relation = models.CharField(max_length=200)
    phone_number = models.CharField(max_length=11)
    email = models.CharField(max_length=200)
    volunteer = models.ForeignKey('Volunteer', on_delete=models.CASCADE)

class VolunteerConditions(models.Model):
    name = models.CharField(max_length=200)
    disclosures = models.TextField()
    volunteer = models.ForeignKey('Volunteer', on_delete=models.CASCADE)

class VolunteerInterest(models.Model):
    tag = models.ForeignKey('opportunities.Tag', on_delete=models.CASCADE)
    volunteer = models.ForeignKey('Volunteer', on_delete=models.CASCADE)

class VolunteerSupplementaryInfo():
    last_updated = models.DateField()
    data = models.CharField(max_length=200)
    volunteer = models.ForeignKey('Volunteer', on_delete=models.CASCADE)
    info = models.ForeignKey('SupplementaryInfo', on_delete=models.CASCADE)

class SupplementaryInfo():
    title = models.CharField(max_length=200)
    description =  models.CharField(max_length=200)

class SupplementaryInfoGrantee():
    org = models.ForeignKey('organisations.Organisation', on_delete=models.CASCADE)
    info = models.ForeignKey('SupplementaryInfo', on_delete=models.CASCADE)
