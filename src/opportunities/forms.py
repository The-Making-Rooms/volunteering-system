from django.forms import ModelForm
from django import forms
from volunteer.models import VolunteerSupplementaryInfo, SupplementaryInfo
import datetime

class SuppInfoForm(ModelForm):

    data = forms.CharField(label='Data', max_length=200, required=True, widget=forms.TextInput(attrs={'placeholder': 'Type Here...', 'style': 'width: 300px;', 'class': 'form-control input w-full max-w-xs mt-3'}))
    
    def __init__(self, *args, **kwargs):
        super(SuppInfoForm, self).__init__(*args, **kwargs)
        self.fields['info'].widget = forms.HiddenInput()

        #tables were smashed and brain cels died but it works...
        #-------------------------------------------------------
        if kwargs.get('initial'):
            self.fields['info'].initial = kwargs.get('initial')
            self.fields['info'].label = kwargs.get('initial')['info'].title
            self.fields['data'].label = kwargs.get('initial')['info'].description
        #-------------------------------------------------------

        

    class Meta:
        model = VolunteerSupplementaryInfo
        fields = ['info', 'data']








