from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django.forms import Form, ModelForm

from bootleg.logging import logging

METHOD_GET = "GET"


def get_default_form_helper(submit_text, inline=False, method="POST"):
    helper = FormHelper()
    helper.add_input(Submit('submit', submit_text, css_class="loading-button"))
    helper.form_method = method
    if inline:
        helper.form_class = 'form-inline'
    return helper


class BaseForm(Form):
    inline = False
    method = "POST"
    logger = logging.get_logger("forms")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.submit_text:
            raise ValueError("Please specify self.submit_text for the form")
        self.helper = get_default_form_helper(self.submit_text, self.inline, self.method)
        self.set_focus()

    # seems like the best method to override for logging errors?!
    def is_valid(self):
        self.log_form_errors()
        return super().is_valid()

    def log_form_errors(self):
        if self.errors:
            self.logger.warning("[%s] Errors: [%s] " % (self.__class__, self.errors.as_data()))

    def add_attribute(self, field, key, value):
        field.widget.attrs.update({key: value})

    def add_class(self, field, klass):
        field.widget.attrs["class"] += " " + klass

    def set_focus(self):
        # set autofocus on the first field
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'autofocus'
            return


class BaseModelForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = forms.get_default_form_helper()
