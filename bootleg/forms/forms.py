from crispy_forms.helper import FormHelper

from bootleg.forms.base import METHOD_GET, BaseForm, get_default_form_helper
from django.forms import CharField, modelform_factory, SelectMultiple, Select
from django.utils.translation import ugettext as _


def get_model_filter_form(model, request):
    form = modelform_factory(model, fields=model._meta.filter_fields)
    # set initial values ... modelform_factory doesn't accept any initial values
    for field in form.base_fields:
        value = request.GET.get(field, None)
        if value:
            form.base_fields[field].initial = value
        # make all fields not-required
        form.base_fields[field].required = False
        # don't allow any multiple selects
        if isinstance(form.base_fields[field].widget, SelectMultiple):
            form.base_fields[field].widget = Select()

    helper = FormHelper()
    helper.form_method = "GET"
    helper.form_id = "bootleg_model_filter_form"
    form.helper = helper
    return form


class GenericModelSearchForm(BaseForm):
    q = CharField(label="", max_length=150, required=False)
    submit_text = _("Search")
    inline = True
    method = METHOD_GET

    def __init__(self, request=None, model=None):
        self.model = model
        if request.GET:
            super().__init__(request.GET or None)
        else:
            super().__init__()
        self.fix_autocomplete()

    def fix_autocomplete(self):
        if self.model.get_autocomplete_url():
            self.add_attribute(self.fields["q"], "data-autocomplete-url", self.model.get_autocomplete_url)
            self.add_attribute(self.fields["q"], "placeholder", _("Search"))
            self.add_class(self.fields["q"], "generic-autocomplete")
            self.add_class(self.fields["q"], "form-control")
