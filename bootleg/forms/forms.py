from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django.db.models import ForeignKey, ManyToManyField
from django.forms import CharField, modelform_factory, SelectMultiple, Select, DateField, \
    DateTimeField, IntegerField, ModelChoiceField, DecimalField, BooleanField, ModelMultipleChoiceField, URLField, \
    SlugField, NullBooleanField
from django.utils.translation import ugettext as _

from bootleg.utils.models import get_order_by

try:
    from django_enumfield.forms.fields import EnumChoiceField
    # ncab are using EnumChoiceField ... somewhat tricky to deal with
    ENUM_FIELD = EnumChoiceField
except ModuleNotFoundError:
    ENUM_FIELD = None
    pass

from bootleg.forms.base import METHOD_GET, BaseForm

EMPTY_LABEL = "---------"


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


class ModelFilterFormFactory:

    def __init__(self, model, request):
        self.model = model
        self.request = request
        self.form = modelform_factory(model, fields=model._meta.filter_fields)
        self.fix_fields()
        self.add_form_helper()
        self.sort_fields()

    def fix_fields(self):
        for field_name in self.form.base_fields:
            # clear initial values (the inputs use the field's default value)
            self.form.base_fields[field_name].initial = None
            # and set the initial value from the request
            value = self.request.GET.get(field_name, None)
            if value:
                self.form.base_fields[field_name].initial = value
            # make all fields not-required
            self.form.base_fields[field_name].required = False
            # set queryset
            queryset = get_queryset_for_field(self.model, field_name)
            if queryset:
                self.form.base_fields[field_name].queryset = queryset

            field = self.model._meta.get_field(field_name)
            # don't allow any multiple selects
            if isinstance(self.form.base_fields[field_name].widget, SelectMultiple):
                self.form.base_fields[field_name].widget = Select()
                self.form.base_fields[field_name].empty_label = EMPTY_LABEL

            # don't allow textareas
            '''
            if isinstance(form.base_fields[field].widget, Textarea):
                form.base_fields[field].widget = CharField
            '''

    def add_form_helper(self):
        helper = FormHelper()
        helper.form_method = "GET"
        helper.form_id = "bootleg_model_filter_form"
        helper.attrs = {"data-model": self.model._meta.model_name}
        helper.add_input(Submit('submit', _("Filter")))
        self.form.helper = helper

    def sort_fields(self):
        sort_order = []
        if ENUM_FIELD:
            sort_order = [ENUM_FIELD]
        sort_order += [ModelChoiceField, ModelMultipleChoiceField, BooleanField, NullBooleanField, DateField,
                       DateTimeField,
                      CharField, IntegerField, DecimalField, URLField, SlugField]

        sorted_fields = sorted(self.form.base_fields.items(), key=lambda pair: sort_order.index(pair[1].__class__))
        fields = dict()
        for field in sorted_fields:
            fields[field[0]] = field[1]
        self.form.base_fields = fields


def get_queryset_for_field(model, field_name):
    field = model._meta.get_field(field_name)

    if isinstance(field, ForeignKey):
        # only use "related" (values that actually have been used) models
        ids = list(model.objects.exclude(**{"%s_id" % field_name: None}).distinct().values_list("%s_id" % field_name,
                                                                                             flat=True))
        return field.related_model.objects.filter(id__in=ids).order_by(*get_order_by(field.related_model))

    if isinstance(field, ManyToManyField):
        # 2020-12-07: I'm not sure this actually works, in the long run. But it works. As of now.
        return field.related_model.objects.filter(**{"%s__isnull" % model._meta.model_name: False})\
            .all().order_by(*get_order_by(field.related_model))
