from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django.forms import Form, ModelForm, BaseForm

from bootleg.logging import logging
from django.utils.translation import ugettext as _

METHOD_GET = "GET"


def get_default_form_helper(submit_text, inline=False, method="POST", css_class=None):
    clazz = "btn-primary"
    if css_class:
        clazz = css_class
    helper = FormHelper()
    helper.add_input(Submit('submit', submit_text, css_class="loading-button %s" % clazz))
    helper.form_id = "bootleg_form"
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
    logger = logging.get_logger("forms", "bootleg.forms")
    submit_text = _("Submit")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = get_default_form_helper(self.submit_text, self.inline, self.method)

    def has_submitted_value(self, request):
        for field in self.fields:
            if self.method == "POST":
                if request.POST.get(field):
                    return True
            if self.method == "GET":
                if request.GET.get(field):
                    return True

        return False

    def add_attribute(self, field, key, value):
        field.widget.attrs.update({key: value})

    def add_class(self, field, klass):
        if "class" not in field.widget.attrs:
            field.widget.attrs["class"] = klass
        else:
            field.widget.attrs["class"] += " " + klass

    def is_search_form(self):
        if len(self.fields) == 1 and "q" in self.fields:
            return True
        return False


class BaseModelForm(ModelForm, BaseForm):
    submit_text = _("Save")
    pass
