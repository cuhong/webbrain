from bootstrap4_datetime.widgets import DateTimePicker
from django import forms
from django.utils import timezone

from participate.models import Participate


class ResearchAgreeForm(forms.ModelForm):
    class Meta:
        model = Participate
        fields = ['agree_name', 'agree_date']

    agree_date = forms.DateField(widget=DateTimePicker(options={'format': "YYYY-MM-DD", "pickTime": False}), initial=timezone.now().date(), label='동의일자')