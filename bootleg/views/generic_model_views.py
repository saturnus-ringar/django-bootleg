from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.urls import reverse
from django.utils.translation import ugettext as _
from django.views.generic import RedirectView, DetailView
from django_tables2 import SingleTableView, RequestConfig

from bootleg.forms.forms import GenericModelSearchForm
from bootleg.utils import models, tables
from bootleg.utils.utils import get_meta_class_value
from bootleg.views.base import BaseCreateUpdateView, BaseCreateView, BaseUpdateView, StaffRequiredView


class GenericModelView(StaffRequiredView):
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
            if get_meta_class_value(self.model, "disable_create_update") is True:
                raise PermissionDenied()

        self.fields = self.model._meta.visible_fields
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        # needed to make django not crash... :|
        self.object = None
        context = super().get_context_data(**kwargs)
        # can't access _meta in them templates...
        context["model"] = models.get_model_dict(self.model)
        return context


class GenericListView(GenericModelView, SingleTableView):
    paginate_by = 25
    template_name = "bootleg/list_view.html"

    def dispatch(self, request, *args, **kwargs):
        self.set_extra_form(request)
        return super().dispatch(request, *args, **kwargs)

    def set_extra_form(self, request):
        if hasattr(self, "extra_form_class"):
            data = self.request.POST
            if self.extra_form_class.method == "GET":
                data = self.request.GET

            if self.extra_form_class().has_submitted_value(request):
                self.extra_form = self.extra_form_class(data)
            else:
                self.extra_form = self.extra_form_class()

    def get_table_class(self):
        return tables.get_default_table(self.model)

    def get_table(self, **kwargs):
        table = super().get_table(**kwargs)
        return RequestConfig(self.request, paginate=self.get_table_pagination(table)).configure(table)

    def get_queryset(self):
        queryset = None
        if "q" in self.request.GET:
            queryset = models.search(self.model, self.model._meta.search_fields, self.request.GET.get("q"))

        if not queryset:
            args = self.get_args()
            if args:
                # got args... filter
                queryset = self.model.objects.filter(**args)

        if not queryset:
            queryset = self.model.objects.all().order_by(*self.get_order_by())

        return queryset.select_related(*self.model.get_foreign_key_field_names())

    def get_order_by(self):
        if hasattr(self.model._meta, "ordering") and self.model._meta.ordering:
            return self.model._meta.ordering
        return ["-id"]

    def get_args(self):
        # dynamic filtering on model properties
        args = dict()
        field_names = self.model.get_all_field_names()
        for param in self.request.GET:
            if param in field_names:
                args[param] = self.request.GET.get(param)

        return args

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if hasattr(self.model._meta, "search_fields"):
            context["form"] = GenericModelSearchForm(self.request, model=self.model)
        if hasattr(self, "extra_form"):
            context["extra_form"] = self.extra_form
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
