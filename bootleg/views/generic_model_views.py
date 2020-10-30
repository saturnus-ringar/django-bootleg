from django.core.exceptions import PermissionDenied
from django.urls import reverse
from django_tables2 import SingleTableView, RequestConfig

from bootleg.forms.forms import GenericModelSearchForm
from bootleg.utils import models
from bootleg.views import views
from bootleg.views.base import BaseCreateUpdateView, BaseCreateView, BaseUpdateView
from django.utils.translation import ugettext as _


class GenericModelView:
    # set this so django doesn't crash with a ... "without the 'fields' attribute is prohibited."
    fields = ["id"]

    def dispatch(self, request, *args, **kwargs):
        model = models.get_editable_by_name(kwargs["model_name"])
        if model:
            self.model = model
        else:
            raise PermissionDenied()

        self.fields = self.model._meta.visible_fields
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # can't access _meta in them templates...
        context["model"] = models.get_model_dict(self.model)
        return context


class GenericListView(GenericModelView, SingleTableView):
    paginate_by = 25
    template_name = "bootleg/list_view.html"

    def get_table_class(self):
        return views.get_default_table(self.model)

    def get_table(self, **kwargs):
        table = super().get_table(**kwargs)
        return RequestConfig(self.request, paginate=self.get_table_pagination(table)).configure(table)

    def get_queryset(self):
        query = self.request.GET.get("q")
        if query:
            return models.search(self.model, self.model._meta.search_fields, query)

        return self.model.objects.all().order_by("id")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if hasattr(self.model._meta, "search_fields"):
            context["form"] = GenericModelSearchForm(self.request, model=self.model)
        return context


class GenericModelCreateUpdateView(GenericModelView, BaseCreateUpdateView):

    def get_success_url(self):
        return reverse("bootleg:list_view", args=[self.model._meta.model_name])


class GenericModelCreateView(GenericModelCreateUpdateView, BaseCreateView):

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        self.heading = _("Create") + " " + self.model._meta.verbose_name
        return response


class GenericModelUpdateView(GenericModelCreateUpdateView, BaseUpdateView):

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        self.heading = _("Create") + " " + self.model._meta.verbose_name
        return response