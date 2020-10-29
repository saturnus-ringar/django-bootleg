from django import forms
from django.contrib.auth.forms import PasswordChangeForm, PasswordResetForm, SetPasswordForm, AuthenticationForm
from django.utils.translation import ugettext as _

from bootleg.forms.base import BaseForm


class BasePasswordForm(BaseForm):
    submit_text = _("Change password")


class CustomSetPasswordForm(BasePasswordForm, PasswordChangeForm):
    pass


class CustomPasswordResetForm(BasePasswordForm, PasswordResetForm):
    submit_text = _("Reset password")


class CustomResetPasswordForm(BasePasswordForm, SetPasswordForm):
    pass


class LoginForm(BaseForm, AuthenticationForm):
    submit_text = _("Login")
    username = forms.CharField(label=_("Email or username"), max_length=150)
    next = forms.CharField(widget=forms.HiddenInput(), required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = kwargs.pop("request")
        self.fields["next"].initial = self.request.GET.get("next", "")
