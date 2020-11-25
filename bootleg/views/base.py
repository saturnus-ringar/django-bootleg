from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.urls import reverse_lazy, reverse
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext as _
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import CreateView, UpdateView, TemplateView

from bootleg.conf import bootleg_settings
from bootleg.forms.base import get_default_form_helper


class StaffRequiredView:

    @method_decorator(staff_member_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class BaseView:
    template_name = bootleg_settings.BASE_TEMPLATE
    page_title = None
    heading = None
    template_name = None
    extra_text = None


class BaseTemplateView(BaseView, TemplateView):
    template_name = bootleg_settings.BASE_TEMPLATE

    def get_extra_text(self):
        return self.extra_text


class StaffRequiredTemplateView(StaffRequiredView, TemplateView):
    pass


class BaseCreateUpdateView(BaseView):
    template_name = bootleg_settings.BASE_TEMPLATE
    success_url = reverse_lazy("bootleg:index")

    def get_form(self, *args, **kwargs):
        form = super().get_form(*args, **kwargs)
        form.helper = get_default_form_helper(self.submit_button_text)
        return form


class BaseCreateView(BaseCreateUpdateView, CreateView):
    model = None
    submit_button_text = _("Save")

    def get_success_url(self):
        if self.type:
            reverse("created") + "?model=%s" % self.model.model_name

    def form_valid(self, form):
        message = _("The %s was added" % self.model._meta.verbose_name)
        messages.add_message(self.request, messages.INFO, message)
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if not hasattr(self, "heading") or self.heading is None:
            context["heading"] = _("Create %s" % self.model._meta.verbose_name)
        if not hasattr(self, "page_title") or self.page_title is None:
            context["page_title"] = _("Create %s" % self.model._meta.verbose_name)
        return context


class BaseUpdateView(BaseCreateUpdateView, UpdateView):
    model = None
    submit_button_text = _("Update")

    def form_valid(self, form):
        message = _("The %s was updated" % self.model._meta.verbose_name)
        messages.add_message(self.request, messages.INFO, message)
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if not hasattr(self, "heading") or self.heading is None:
            context["heading"] = _("Update %s" % self.model._meta.verbose_name)
        if not hasattr(self, "page_title") or self.page_title is None:
            context["page_title"] = _("Update %s" % self.model._meta.verbose_name)
        return context


class CSRFExemptView(View):

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class FormWithRequestMixin(View):

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({'request': self.request})
        return kwargs
