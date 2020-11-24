from bootleg.utils import models
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from django_tables2 import tables

from bootleg.views.base import BaseTemplateView, StaffRequiredTemplateView


def get_default_table(model):
    if hasattr(model._meta, "visible_fields"):
        fields = model._meta.visible_fields
    else:
        fields = model._meta.fields
    table_class = tables.table_factory(model, fields=fields + ["get_update_link"])
    table_class._meta.attrs["class"] = "table table-striped table-responsive table-hover w-100 d-block d-md-table"
    return table_class


class CreatedView(BaseTemplateView):

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        model = models.get_editable_by_name(self.request.GET.get("model"))
        context["title"] = model().get_created_title()
        context["heading"] = model().get_created_title()
        context["extra_text"] = model().get_created_text()
        return context


class DevNullView(BaseTemplateView):
    template_name = "bootleg/dev_null.html"
    title = _("dev/null")
    heading = _("dev/null")

    def dispatch(self, request, *args, **kwargs):
        messages.info(request, _("Since you can read this - it probably means the site is up and running?!?!?!?!"))
        return super().dispatch(request, args, kwargs)


class CrashView(StaffRequiredTemplateView):

    def dispatch(self, request, *args, **kwargs):
        0 / 0
