from django.forms import ModelForm
from organisations.models import Organisation, Location, Image, Video


class OrganisationLocationForm(ModelForm):
    class Meta:
        model = Location
        fields = ['organisation', 'name', 'description', 'first_line', 'second_line', 'postcode', 'city']
