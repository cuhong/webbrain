from django.contrib.admin.forms import AdminAuthenticationForm
from django.contrib.auth.forms import AuthenticationForm
from django import forms

from research.models import Poll


class ResearchAdminAuthenticationForm(AdminAuthenticationForm):
    """
    is_researcher = True 인 유저만 접근 가능하도록 기존 AdminAuthenticationForm
    오버라이딩
    """
    error_messages = {
        **AuthenticationForm.error_messages,
        'invalid_login': "연구원 사용자가 아닙니다.",
    }
    required_css_class = 'required'

    def confirm_login_allowed(self, user):
        if not user.is_researcher:
            raise forms.ValidationError(
                self.error_messages['invalid_login'],
                code='invalid_login',
                params={'username': self.username_field.verbose_name}
            )


