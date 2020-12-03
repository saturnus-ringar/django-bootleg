from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _
from django_tables2 import tables, Column, BooleanColumn

from bootleg.utils.utils import get_meta_class_value


def add_initial_columns(model, table_class):
    initial_column_names = []
    if hasattr(model, "get_initial_columns"):
        initial_columns = model.get_initial_columns()
        for initial_column in initial_columns:
            initial_column_names.append(initial_column[0])
        table_class.base_columns.update(initial_columns)
        for column_name in initial_column_names:
            table_class.base_columns.move_to_end(column_name, last=False)

    return initial_column_names


def get_default_table(model):
    if hasattr(model._meta, "visible_fields"):
        fields = model._meta.visible_fields
    else:
        fields = model._meta.fields

    table_class = tables.table_factory(model, fields=fields)
    table_class._meta.attrs["class"] = "table table-striped table-responsive table-hover w-100 d-block d-md-table"

    end_fields = ["detail"]
    if not get_meta_class_value(model, "disable_create_update") is True:
        end_fields.append("update")
    if get_meta_class_value(model, "allow_deletion"):
        end_fields.append("delete")

    initial_columns = add_initial_columns(model, table_class)

    if get_meta_class_value(model, "cloneable") is True:
        table_class.base_columns.update([("clone", Column(accessor="get_clone_link", verbose_name=_("Clone"),
                                                          orderable=False))])
        end_fields.append("clone")

    table_class.base_columns.update([("detail", Column(accessor="get_detail_link", verbose_name=_("View"),
                                                       orderable=False))])
    if not get_meta_class_value(model, "disable_create_update") is True:
        table_class.base_columns.update([("update", Column(accessor="get_update_link", verbose_name=_("Update"),
                                                           orderable=False))])
    if get_meta_class_value(model, "allow_deletion"):
        table_class.base_columns.update([("delete", Column(accessor="get_delete_link", verbose_name=_("Delete"),
                                                           orderable=False))])
    table_class._meta.sequence = (initial_columns + fields + end_fields)
    return table_class


def render_boolean_colum(self, value, record, bound_column):
    value = self._get_bool_value(record, value, bound_column)
    if value:
        text = _("Yes")
        css_class = "success"
    else:
        text = _("No")
        css_class = "danger"

    return mark_safe('<span class="label label-%s">%s</span>' % (css_class, text))

# monkey patch Django table 2's boolean column-rendering
BooleanColumn.render = render_boolean_colum
