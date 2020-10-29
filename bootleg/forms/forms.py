from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django.forms import CharField
from django.utils.translation import ugettext as _

from bootleg.forms.base import BaseForm, METHOD_GET


def get_default_form_helper(submit_text, inline=False, method="POST"):
    helper = FormHelper()
    helper.add_input(Submit('submit', submit_text, css_class="loading-button"))
    helper.form_method = method
    if inline:
        helper.form_class = 'form-inline'
    return helper


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
            self.add_class(self.fields["q"], "generic-autocomplete")
