from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django.db.models import ForeignKey, ManyToManyField
from django.forms import CharField, modelform_factory, SelectMultiple, Select, DateField, \
    DateTimeField, IntegerField, ModelChoiceField, DecimalField, BooleanField, ModelMultipleChoiceField, Textarea
from django.utils.translation import ugettext as _

try:
    from django_enumfield.forms.fields import EnumChoiceField
    # ncab are using EnumChoiceField ... somewhat tricky to deal with
    ENUM_FIELD = EnumChoiceField
except ModuleNotFoundError:
    ENUM_FIELD_IMPORTED = None
    pass

from bootleg.forms.base import METHOD_GET, BaseForm

EMPTY_LABEL = "---------"


def sort_fields(fields):
    sort_order = [ModelChoiceField, ModelMultipleChoiceField, ENUM_FIELD, BooleanField, DateField, DateTimeField,
                  CharField, IntegerField, DecimalField]
    sorted_fields = sorted(fields.items(), key=lambda pair: sort_order.index(pair[1].__class__))
    fields = dict()
    for field in sorted_fields:
        fields[field[0]] = field[1]
    return fields


def get_model_filter_form(model, request):
    form = modelform_factory(model, fields=model._meta.filter_fields)
    # set initial values ... modelform_factory doesn't accept any initial values
    for field in form.base_fields:
        # clear initial values (the inputs use the field's default value)
        form.base_fields[field].initial = None
        # and set the initial value from the request
        value = request.GET.get(field, None)
        if value:
            form.base_fields[field].initial = value
        # make all fields not-required
        form.base_fields[field].required = False
        # set queryset
        queryset = get_queryset_for_field(model, field)
        if queryset:
            form.base_fields[field].queryset = queryset

        # don't allow any multiple selects
        if isinstance(form.base_fields[field].widget, SelectMultiple):
            form.base_fields[field].widget = Select()
            form.base_fields[field].empty_label = EMPTY_LABEL

        # don't allow textareas
        '''
        if isinstance(form.base_fields[field].widget, Textarea):
            form.base_fields[field].widget = CharField
        '''

    form.base_fields = sort_fields(form.base_fields)
    # add form helper
    helper = FormHelper()
    helper.form_method = "GET"
    helper.form_id = "bootleg_model_filter_form"
    helper.attrs = {"data-model": model._meta.model_name}
    helper.add_input(Submit('submit', _("Filter")))
    form.helper = helper
    return form


def get_queryset_for_field(model, field_name):
    field = model._meta.get_field(field_name)
    if isinstance(field, ForeignKey):
        # only use "related" (values that actually have been used) models
        ids = list(model.objects.exclude(**{"%s_id" % field_name: None}).distinct().values_list("%s_id" % field_name,
                                                                                             flat=True))
        return field.related_model.objects.filter(id__in=ids)

    if isinstance(field, ManyToManyField):
        # 2020-12-07: I'm not sure this actually works, in the long run. But it works. As of now.
        return field.related_model.objects.filter(**{"%s__isnull" % model._meta.model_name: False}).all()


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
