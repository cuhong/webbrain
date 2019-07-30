from django import forms


class ResearchAgreeForm(forms.Form):
    name = forms.CharField()
    date = forms.DateField(input_formats=['%Y-%m-%d'])