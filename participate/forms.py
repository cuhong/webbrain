from django import forms
from django.utils import timezone

from participate.models import Participate


class ResearchAgreeForm(forms.ModelForm):
    class Meta:
        model = Participate
        fields = ['agree_name', 'agree_date']

    agree_date = forms.DateField(input_formats=['%Y-%m-%d'], initial=timezone.now().date(), label='동의일자')