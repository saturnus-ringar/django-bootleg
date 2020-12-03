from django.contrib import messages
from django.core.exceptions import SuspiciousOperation, PermissionDenied
from django.http import Http404
from django.utils.translation import ugettext_lazy as _

from bootleg.utils import models
from bootleg.views.base import BaseTemplateView, StaffRequiredTemplateView


class CreatedView(BaseTemplateView):

    def dispatch(self, request, *args, **kwargs):
        self.model = kwargs["model_name"]
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        model = models.get_editable_by_name(self.model)
        context["page_title"] = model().get_created_title()
        context["heading"] = model().get_created_title()
        context["extra_text"] = model().get_created_text()
        return context


class DevNullView(BaseTemplateView):
    template_name = "bootleg/dev_null.html"
    page_title = _("dev/null")
    heading = _("dev/null")

    def dispatch(self, request, *args, **kwargs):
        messages.info(request, _("Since you can read this - it probably means the site is up and running."))
        return super().dispatch(request, args, kwargs)


class CrashView(StaffRequiredTemplateView):

    def dispatch(self, request, *args, **kwargs):
        0 / 0


class ErrorTestView(StaffRequiredTemplateView):
    template_name = "bootleg/base.html"

    def dispatch(self, request, *args, **kwargs):
        self.error_code = int(kwargs["error_code"])
        if self.error_code == 400:
            raise SuspiciousOperation("Bad request test.")
        elif self.error_code == 403:
            raise PermissionDenied("Permission denied test.")
        elif self.error_code == 404:
            raise Http404("404 test.")
        elif self.error_code == 500:
            raise Exception("500 test.")

        return super().dispatch(request, *args, **kwargs)
