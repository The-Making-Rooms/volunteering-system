from django.forms import ModelForm
from .models import OrgnaisationAdmin
from opportunities.models import *
from organisations.models import *

class OrganisationDetailsForm(ModelForm):
    class Meta:
        model = Organisation
        fields = ['name', 'description']

class OrganisationLocationForm(ModelForm):
    class Meta:
        model = Location
        fields = ['name', 'description', 'first_line', 'second_line', 'postcode', 'city']

class OrganisationImageForm(ModelForm):
    class Meta:
        model = Image
        fields = ['image']

class OrgnaisationVideoForm(ModelForm):
    class Meta:
        model = Video
        fields = ['video']
    
class OrgnaisationLinkForm(ModelForm):
    class Meta:
        model = Link
        fields = ['name', 'link', 'icon', 'description']