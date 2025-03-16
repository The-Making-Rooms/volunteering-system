"""
VolunteeringSystem

This project is distributed under the CC BY-NC-SA 4.0 license. See LICENSE for details.
"""

from django.forms import ModelForm
from organisations.models import Organisation, Location
from opportunities.models import Opportunity, Location as OpportunityLocation



class OpportunityForm(ModelForm):
    class Meta:
        model = Opportunity
        fields = ['name', 'description', 'organisation']

class opportunityReccurenceForm(ModelForm):
    class Meta:
        model = Opportunity
        fields = ['recurrences']