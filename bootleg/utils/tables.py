from django.utils.safestring import mark_safe
from django_tables2 import tables, Column, BooleanColumn
from django.utils.translation import ugettext as _
from bootleg.utils.utils import get_meta_class_value


def add_columns(model, table_class, method):
    column_names = []
    if hasattr(model, method):
        columns = getattr(model, method)()
        for column in columns:
            column_names.append(column[0])
        table_class.base_columns.update(columns)
        for column_name in column_names:
            table_class.base_columns.move_to_end(column_name, last=False)

    return column_names


def get_end_field_list(model):
    # set the fields that we want at the end of the table
    end_fields = []
    if hasattr(model(), "get_absolute_url_link"):
        end_fields = ["absolute_url"]

    if not get_meta_class_value(model, "disable_create_update") is True:
        end_fields.append("update")
    if get_meta_class_value(model, "allow_deletion"):
        end_fields.append("delete")

    return end_fields


def get_default_table(model):
    # get all visible fields
    if hasattr(model._meta, "visible_fields"):
        fields = model._meta.visible_fields
    else:
        fields = model._meta.fields

    table_class = tables.table_factory(model, fields=fields)
    table_class._meta.attrs["class"] = "table table-striped table-responsive table-hover w-100 d-block d-md-table"

    # add initial and additional columns
    initial_columns = ["detail"] + add_columns(model, table_class, "get_initial_columns")
    additional_columns = add_columns(model, table_class, "get_additional_columns")
    # get end field names
    end_fields = get_end_field_list(model)

    # abolute url link
    if hasattr(model(), "get_absolute_url_link"):
        table_class.base_columns.update([("absolute_url", Column(accessor="get_absolute_url_link", verbose_name=_("URL"),
                                                          orderable=False))])
    # clone link
    if get_meta_class_value(model, "cloneable") is True:
        table_class.base_columns.update([("clone", Column(accessor="get_clone_link", verbose_name=_("Clone"),
                                                          orderable=False))])
        end_fields.append("clone")

    # detail link
    table_class.base_columns.update([("detail", Column(accessor="get_detail_link", verbose_name=_("View"),
                                                       orderable=False))])
    # update links
    if not get_meta_class_value(model, "disable_create_update") is True:
        if hasattr(model(), "get_custom_update_link"):
            table_class.base_columns.update([("update", Column(accessor="get_custom_update_link",
                                                               verbose_name=_("Update"), orderable=False))])
        else:
            table_class.base_columns.update([("update", Column(accessor="get_update_link", verbose_name=_("Update"),
                                                               orderable=False))])
    # deletion links
    if get_meta_class_value(model, "allow_deletion"):
        table_class.base_columns.update([("delete", Column(accessor="get_delete_link", verbose_name=_("Delete"),
                                                           orderable=False))])
    table_class._meta.sequence = (initial_columns + fields + additional_columns + end_fields)
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
