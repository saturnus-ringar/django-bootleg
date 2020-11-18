from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django.forms import Form, ModelForm, BaseForm

from bootleg.logging import logging
from django.utils.translation import ugettext as _

METHOD_GET = "GET"


def get_default_form_helper(submit_text, inline=False, method="POST"):
    helper = FormHelper()
    helper.add_input(Submit('submit', submit_text, css_class="loading-button"))
    helper.form_method = method
    if inline:
        helper.form_class = 'form-inline'
    return helper


def log_form_errors(form):
    if form.errors:
        BaseForm.logger.warning("[%s] Errors: [%s] " % (form.__class__.__name__, form.errors.as_data()))


# some dirty monkey patching to log form errors
def monkey_patched_is_valid(self):
    log_form_errors(self)
    return self.is_bound and not self.errors


# set this monkey patched method on Django's BaseForm
BaseForm.is_valid = monkey_patched_is_valid


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


    def add_attribute(self, field, key, value):
        field.widget.attrs.update({key: value})

    def add_class(self, field, klass):
        field.widget.attrs["class"] += " " + klass

    def set_focus(self):
        # set autofocus on the first field
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'autofocus'
            return


class BaseModelForm(ModelForm, BaseForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = get_default_form_helper(_("Save"))
