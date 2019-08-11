from bootstrap_datepicker_plus import DatePickerInput
from django import forms
from django.utils import timezone

from participate.models import Participate


class ResearchAgreeForm(forms.ModelForm):
    class Meta:
        model = Participate
        fields = ['agree_name', 'agree_date']
        widgets = {
            'agree_date': DatePickerInput(format='YYYY-MM-DD')
        }