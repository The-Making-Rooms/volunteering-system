from django.db import models
from django.conf import settings

# Create your models here.
class Volunteer(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatars/', blank=True)
    date_of_birth = models.DateField()
    phone_number = models.CharField(max_length=11)
    bio = models.TextField()
    CV = models.FileField(upload_to='CV/', blank=True)

    def __str__(self):
        return self.user.first_name + ' ' + self.user.last_name + ' (' + self.user.email + ')'

class VolunteerAddress(models.Model):
    first_line = models.CharField(max_length=200)
    second_line = models.CharField(max_length=200, blank=True, null=True)
    postcode = models.CharField(max_length=200)
    city = models.CharField(max_length=200)
    volunteer = models.ForeignKey('Volunteer', on_delete=models.CASCADE)


class VolunteerSupplementaryInfo(models.Model):
    last_updated = models.DateField()
    data = models.CharField(max_length=200)
    volunteer = models.ForeignKey('Volunteer', on_delete=models.CASCADE)
    info = models.ForeignKey('SupplementaryInfo', on_delete=models.CASCADE)

class EmergencyContacts(models.Model):
    name = models.CharField(max_length=200)
    relation = models.CharField(max_length=200)
    phone_number = models.CharField(max_length=11)
    email = models.CharField(max_length=200)
    volunteer = models.ForeignKey('Volunteer', on_delete=models.CASCADE)

class VolunteerConditions(models.Model):
    disclosures = models.TextField()
    volunteer = models.ForeignKey('Volunteer', on_delete=models.CASCADE)

class VolunteerInterest(models.Model):
    tag = models.ForeignKey('opportunities.Tag', on_delete=models.CASCADE)
    volunteer = models.ForeignKey('Volunteer', on_delete=models.CASCADE)

class SupplementaryInfo(models.Model):
    title = models.CharField(max_length=200)
    description =  models.CharField(max_length=200)
    organisation = models.ForeignKey('organisations.Organisation', on_delete=models.CASCADE, null=True)

class SupplementaryInfoGrantee(models.Model):
    org = models.ForeignKey('organisations.Organisation', on_delete=models.CASCADE)
    info = models.ForeignKey('VolunteerSupplementaryInfo', on_delete=models.CASCADE)
    volunteer = models.ForeignKey('Volunteer', on_delete=models.CASCADE)
