from django.contrib import messages
from django.contrib.auth import update_session_auth_hash, logout
from django.contrib.auth.views import LoginView, PasswordResetView, PasswordResetConfirmView
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse, reverse_lazy
from django.utils.translation import ugettext as _

from bootleg.conf import settings
from bootleg.forms.auth_forms import CustomPasswordResetForm, CustomResetPasswordForm, CustomSetPasswordForm, LoginForm
from bootleg.views.base import BaseTemplateView, FormWithRequestMixin


class LogoutView(BaseTemplateView):
    title = _("Logout")
    text = _("You have been logged out")

    def get(self, request, *args, **kwargs):
        logout(request)
        return super().get(self, request, *args, **kwargs)


class CustomLoginView(BaseTemplateView, LoginView, FormWithRequestMixin):
    form_class = LoginForm
    # can't do it like this:
    # extra_text = _('<a href="%s">Forgot password?</a>' % reverse_lazy("password_reset"))
    # ... end up getting this:
    # django.core.exceptions.ImproperlyConfigured: The included URLconf 'django_tango.urls' does not appear to have any
    # patterns in it. If you see valid patterns in the file then the issue is probably caused by a circular import.

    def get_success_url(self):
        next_url = self.request.POST.get("next", "")
        if next_url:
            return next_url
        return settings.login_redirect_url()

    def get_extra_text(self):
        return _('<a href="%s">Forgot password?</a>' % reverse_lazy("password_reset"))


class PasswordResetBaseView(BaseTemplateView):
    title = _("Reset password")


class CustomPasswordResetView(PasswordResetBaseView, PasswordResetView):
    form_class = CustomPasswordResetForm
    email_template_name = "bootleg/registration/password_reset_email.html"
    subject_template_name = "bootleg/registration/password_reset_subject.txt"


class CustomPasswordResetConfirmView(PasswordResetBaseView, PasswordResetConfirmView):
    form_class = CustomResetPasswordForm


class CustomPasswordResetCompleteView(PasswordResetBaseView):

    def get_extra_text(self):
        return _('Your password has been set.<p class="mt-4"><a href="%s">Go to login</a></p>' % reverse("login"))


def change_password(request):
    if request.method == 'POST':
        form = CustomSetPasswordForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, _("Your password was changed."))
            return redirect('change_password')
    else:
        form = CustomSetPasswordForm(request.user)

    context = {}
    context["form"] = form
    context["title"] = _("Change password")
    return render(request, 'website/base.html', context)
