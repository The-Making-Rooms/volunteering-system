from django.forms import ModelForm
from organisations.models import Organisation, Location
from opportunities.models import Opportunity, Location as OpportunityLocation


class OrganisationLocationForm(ModelForm):
    class Meta:
        model = Location
        fields = ['organisation', 'name', 'description', 'first_line', 'second_line', 'postcode', 'city']
        
class OpportunityLocationForm(ModelForm):
    class Meta:
        model = OpportunityLocation
        fields = ['opportunity', 'name', 'description', 'first_line', 'second_line', 'postcode', 'city']

class OpportunityForm(ModelForm):
    class Meta:
        model = Opportunity
        fields = ['name', 'description', 'organisation']

class opportunityReccurenceForm(ModelForm):
    class Meta:
        model = Opportunity
        fields = ['recurrences']