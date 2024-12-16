"""
VolunteeringSystem

This project is distributed under the CC BY-NC-SA 4.0 license. See LICENSE for details.
"""

from django.forms import ModelForm
from .models import EmergencyContacts, VolunteerAddress, VolunteerConditions, Volunteer

class VolunteerForm(ModelForm):
    class Meta:
        model = Volunteer
        fields = ['avatar', 'date_of_birth', 'phone_number', 'bio', 'CV']
    
class VolunteerAddressForm(ModelForm):
    class Meta:
        model = VolunteerAddress
        fields = ['first_line', 'second_line', 'postcode', 'city']

class EmergencyContactsForm(ModelForm):
    class Meta:
        model = EmergencyContacts
        fields = ['name', 'relation', 'phone_number', 'email']

class VolunteerConditionsForm(ModelForm):
    class Meta:
        model = VolunteerConditions
        fields = ['disclosures']

