from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm


User = get_user_model()


class CustomParticipantUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('email', 'name')

    next = forms.CharField(required=False)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.name = self.cleaned_data['name']
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class CustomStaffUserCreationForm(UserCreationForm):

    def save(self, commit=True):
        user = super().save(commit=False)
        user.name = self.cleaned_data['name']
        user.is_staff = True
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class CustomResearcherUserCreationForm(UserCreationForm):

    def save(self, commit=True):
        user = super().save(commit=False)
        user.name = self.cleaned_data['name']
        user.is_researcher = True
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class CustomLoginView(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email', 'password']
