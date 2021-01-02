from django.core.exceptions import FieldDoesNotExist
from django.db.models import IntegerField
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _
from django_tables2 import tables, Column, BooleanColumn, columns
from humanize import intcomma

from bootleg.utils import lists
from bootleg.utils.utils import get_meta_class_value


def get_id_or_zero(record, field):
    try:
        object = getattr(record, field)
        if object and hasattr(object, "id"):
            return object.id
        if object and hasattr(object, "value"):
            return object.value
        return 0
    except Exception as e:
        return 0


class IntegerColumn(Column):

    def render(self, value):
        return intcomma(value)


class TableFactory:

    def __init__(self, model, request=None):
        self.model = model
        self.model_obj = model()
        self.request = request
        self.table_class = tables.table_factory(self.model, fields=[])
        self.initial_fields = []
        self.base_fields = []
        self.additional_fields = []
        self.request_fields = []
        self.end_fields = []
        self.add_table_attrs()
        self.set_base_fields()
        self.add_request_fields()
        self.add_end_columns()
        self.setup_table_class()
        self.set_sequence()

    def add_table_attrs(self):
        self.table_class._meta.attrs["class"] = "table table-striped table-responsive table-hover w-100 " \
                                                "d-block d-md-table"
        # add object-id attr
        self.table_class._meta.row_attrs = {
            "id": lambda record: "object_row_%s" % record.pk
        }

    def set_base_fields(self):
        # get all visible fields
        visible_fields = self.model.get_visible_fields()
        if visible_fields:
            self.base_fields = visible_fields
        else:
            self.base_fields = self.model._meta.fields

    def add_request_fields(self):
        if self.request:
            for param, value in self.request.GET.items():
                if param in self.model.get_all_field_names():
                    if param not in self.base_fields:
                        self.request_fields.append(param)

    def add_end_columns(self):
        if hasattr(self.model_obj, "get_custom_update_link"):
            self.table_class.base_columns.update([("update", Column(accessor="get_custom_update_link",
                                                verbose_name=_("Update"), orderable=False))])
            self.end_fields.append("update")
        else:
            # update links
            if not get_meta_class_value(self.model, "disable_create_update") is True:
                self.table_class.base_columns.update([("update", Column(accessor="get_update_link",
                                                verbose_name=_("Update"), orderable=False))])
                self.end_fields.append("update")

        # clone link
        if get_meta_class_value(self.model, "cloneable") is True:
            self.table_class.base_columns.update([("clone", Column(accessor="get_clone_link", verbose_name=_("Clone"),
                                                              orderable=False))])
            self.end_fields.append("clone")
        # deletion links
        if get_meta_class_value(self.model, "allow_deletion"):
            self.table_class.base_columns.update([("delete", Column(accessor="get_delete_link", verbose_name=_("Delete"),
                                                               orderable=False))])
            self.end_fields.append("delete")

    def setup_table_class(self):
        for field in self.base_fields + self.request_fields:
            self.add_standard_column(field)

        # add initial and additional columns
        self.initial_fields = ["detail"] + self.add_columns("get_initial_columns")
        self.additional_fields = self.add_columns("get_additional_columns")

        # abolute url link
        if hasattr(self.model, "get_absolute_url_link") and hasattr(self.model_obj, "get_absolute_url"):
            self.table_class.base_columns.update([("absolute_url", Column(accessor="get_absolute_url_link",
                                                verbose_name=_("URL"), orderable=False))])
        # detail link
        self.table_class.base_columns.update([("detail", Column(accessor="get_ajax_detail_link",
                                                verbose_name=_("View"), orderable=False))])

    def set_sequence(self):
        sequence = get_meta_class_value(self.model, "sequence")
        if sequence:
            self.table_class._meta.sequence = self.initial_fields + sequence
        else:
            self.table_class._meta.sequence = self.cleanup_fields()

    def add_columns(self, method):
        field_names = []
        if hasattr(self.model, method):
            columns = getattr(self.model, method)()
            for column in columns:
                field_names.append(column[0])
            self.table_class.base_columns.update(columns)
            for column_name in field_names:
                self.table_class.base_columns.move_to_end(column_name, last=False)

        return field_names

    def cleanup_fields(self):
        cleaned_fields = self.initial_fields
        cleaned_fields = lists.add_unique(cleaned_fields, self.request_fields)
        cleaned_fields = lists.add_unique(cleaned_fields, self.base_fields)
        cleaned_fields = lists.add_unique(cleaned_fields, self.additional_fields)
        cleaned_fields += self.end_fields
        return cleaned_fields

    def add_standard_column(self, field_name):
        attrs = {
            "td": {
                "data-field-name": field_name,
                "data-object-id": lambda record: get_id_or_zero(record, field_name)
            }
        }

        try:
            field = self.model._meta.get_field(field_name)
            if isinstance(field, IntegerField):
                column_class = IntegerColumn
            else:
                column_class = columns.library.column_for_field(field=field).__class__
            name = None
            if hasattr(field, "verbose_name"):
                name = field.verbose_name
            self.table_class.base_columns.update([(field_name, column_class(accessor=field_name,
                                            verbose_name=name, attrs=attrs))])
        except FieldDoesNotExist:
            self.table_class.base_columns.update([(field_name, Column(accessor=field_name, attrs=attrs))])


def render_boolean_column(self, value, record, bound_column):
    value = getattr(record, bound_column.column.accessor)
    if value is True:
        text = _("Yes")
        css_class = "success"
    elif value is False:
        text = _("No")
        css_class = "danger"
    else:
        text = _("Unknown")
        css_class = "warning"

    # progress-bar for bootstrap 3
    return mark_safe('<span class="badge progress-bar-%s badge-%s">%s</span>'
                     % (css_class, css_class, text))

# monkey patch Django table 2's boolean column-rendering
BooleanColumn.render = render_boolean_column
