import json

from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.urls import reverse
from django.utils.translation import ugettext as _
from django.views.generic import RedirectView, DetailView
from django_tables2 import SingleTableView, RequestConfig
from djangoql.serializers import DjangoQLSchemaSerializer

from bootleg.forms.forms import GenericModelSearchForm, ModelFilterFormFactory, DQLSearchForm
from bootleg.search.model_searcher import ModelSearcher
from bootleg.utils import models
from bootleg.utils.env import use_elastic_search
from bootleg.utils.html import get_default_table_class_string
from bootleg.utils.http import get_model_args_from_request
from bootleg.utils.models import GenericDjangoQLSchema, SearchResults
from bootleg.utils.tables import TableFactory
from bootleg.utils.utils import get_meta_class_value
from bootleg.views.base import BaseCreateUpdateView, BaseCreateView, BaseUpdateView


class GenericModelView:
    # set this so django doesn't crash with a ... "without the 'fields' attribute is prohibited."
    fields = ["id"]

    def dispatch(self, request, *args, **kwargs):
        # allow forcing of model
        if not hasattr(self, "model") or not self.model:
            model = models.get_editable_by_name(kwargs["model_name"])
            if model:
                self.model = model
                if "pk" in kwargs:
                    self.object = self.model.objects.get(id=kwargs["pk"])
            else:
                raise Http404("Could not find model.")

        if isinstance(self, GenericModelCreateView) or isinstance(self, GenericModelUpdateView):
            if not self.model.is_allowed_to_edit(self.request.user):
                raise PermissionDenied("You don't have permission to edit this.")

        if not self.model.is_allowed_to_view(self.request.user):
            raise PermissionDenied(_("You don't have permission to view this."))

        self.fields = self.model._meta.visible_fields
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        # needed to make django not crash... :|
        self.object = None
        context = super().get_context_data(**kwargs)
        # can't access _meta in them templates...
        context["model"] = models.get_model_dict(self.model)
        context["model_class"] = self.model
        return context


class GenericListView(GenericModelView, SingleTableView):
    paginate_by = 25
    template_name = "bootleg/list_view.html"

    def get_table_class(self):
        return TableFactory(self.model, self.request).table_class

    def get_paginator(self, *args, **kwargs):
        if hasattr(self.model, "get_paginator_class"):
            self.paginator_class = getattr(self.model, "get_paginator_class")

        paginator = None
        if use_elastic_search():
            doc = self.model.get_search_document()
            if self.model_searcher.search_results:
                paginator = self.paginator_class(self.model_searcher.search_results, self.paginate_by)
            elif doc and not self.model_searcher.is_search():
                # no query args, but got a document
                paginator = self.paginator_class(SearchResults(self.model.get_search_index_total_count_results()),
                                            self.paginate_by)
        if not paginator:
            return super().get_paginator(*args, **kwargs)
        else:
            return paginator

    def get_table(self, **kwargs):
        table = super().get_table(**kwargs)
        table.attrs = {
            "id": "bootleg_list_table",
            "class": get_default_table_class_string()
        }
        return RequestConfig(self.request, paginate=self.get_table_pagination(table)).configure(table)

    def get_queryset(self):
        forced_query = self.request.GET.get("fq", None)
        if forced_query:
            self.paginate_by = 250
        self.model_searcher = ModelSearcher(self.model, query=self.request.GET.get("q", None),
                                dql_query=self.request.GET.get("dql", None),
                                args=get_model_args_from_request(self.model, self.request),
                                es_limit=self.paginate_by, forced_query=forced_query)
        self.model_searcher.search()
        return self.model_searcher.get_queryset()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.model.get_search_field_names():
            context["form"] = GenericModelSearchForm(self.request, model=self.model)
        # djangoql
        introspections = DjangoQLSchemaSerializer().serialize(
            GenericDjangoQLSchema(self.model),
        )
        context["introspections"] = json.dumps(introspections)
        context["dql_form"] = DQLSearchForm(self.request,model=self.model)

        if get_meta_class_value(self.model, "filter_fields"):
            # filter forms
            context["filter_form"] = ModelFilterFormFactory(self.model, self.request).form

        return context


class GenericModelCreateUpdateView(GenericModelView, BaseCreateUpdateView):

    def get_success_url(self):
        return reverse("bootleg:list_view", args=[self.model._meta.model_name])


class GenericModelCreateView(GenericModelCreateUpdateView, BaseCreateView):
    pass


class GenericModelUpdateView(GenericModelCreateUpdateView, BaseUpdateView):

    def get_form_kwargs(self):
        # don't know why, but for some reason self.object is None in get_form_kwargs in
        # ModelFormMixin, set the instance here then...
        kwargs = super().get_form_kwargs()
        kwargs.update({'instance': self.get_object()})
        return kwargs

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        if not hasattr(self, "heading"):
            self.heading = _("Update") + " " + self.model._meta.verbose_name
        return response


class GenericModelCloneView(GenericModelView, RedirectView):

    def get_redirect_url(self, *args, **kwargs):
        self.object.pk = None
        try:
            fix_clone_data = getattr(self.object, "fix_clone_data")
            fix_clone_data()
        except AttributeError:
            pass
        self.object.save()
        messages.add_message(self.request, messages.INFO, _("The %s was cloned" % self.model._meta.verbose_name))
        return self.object.get_update_url()


class GenericModelDeleteView(GenericModelView, RedirectView):

    def get_redirect_url(self, *args, **kwargs):
        if not get_meta_class_value(self.model, "allow_deletion") is True:
            raise PermissionDenied()

        if hasattr(self.object, "log_delete"):
            self.object.log_delete(self.request)
        self.object.delete()
        messages.add_message(self.request, messages.INFO, _("The %s was deleted" % self.model._meta.verbose_name))
        if "HTTP_REFERER" in self.request.META:
            return self.request.META["HTTP_REFERER"]

        return self.object.__class__.get_list_url()


class GenericModelDetailView(GenericModelView, DetailView):
    template_name = "bootleg/detail_view.html"
