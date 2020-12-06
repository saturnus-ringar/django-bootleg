from bootleg.utils import lists
from django.utils.safestring import mark_safe
from django_tables2 import tables, Column, BooleanColumn
from django.utils.translation import ugettext as _
from bootleg.utils.utils import get_meta_class_value


def add_columns(model, table_class, method):
    field_names = []
    if hasattr(model, method):
        columns = getattr(model, method)()
        for column in columns:
            field_names.append(column[0])
        table_class.base_columns.update(columns)
        for column_name in field_names:
            table_class.base_columns.move_to_end(column_name, last=False)

    return field_names


def cleanup_fields(inital_fields, fields, additional_fields, end_fields):
    cleaned_fields = inital_fields
    cleaned_fields = lists.add_unique(cleaned_fields, fields)
    cleaned_fields = lists.add_unique(cleaned_fields, additional_fields)
    cleaned_fields += end_fields
    return cleaned_fields


def get_default_table(model):
    model_obj = model()
    # get all visible fields
    if hasattr(model._meta, "visible_fields"):
        fields = model._meta.visible_fields
    else:
        fields = model._meta.fields

    table_class = tables.table_factory(model, fields=fields)
    table_class._meta.attrs["class"] = "table table-striped table-responsive table-hover w-100 d-block d-md-table"

    # add initial and additional columns
    initial_fields = ["detail"] + add_columns(model, table_class, "get_initial_columns")
    additional_fields = add_columns(model, table_class, "get_additional_columns")

    # abolute url link
    if hasattr(model, "get_absolute_url_link") and hasattr(model_obj, "get_absolute_url"):
        table_class.base_columns.update([("absolute_url", Column(accessor="get_absolute_url_link", verbose_name=_("URL"),
                                                          orderable=False))])
    # detail link
    table_class.base_columns.update([("detail", Column(accessor="get_xhr_detail_link", verbose_name=_("View"),
                                                           orderable=False))])

    end_fields = []
    if hasattr(model(), "get_custom_update_link"):
        table_class.base_columns.update([("update", Column(accessor="get_custom_update_link",
                                                           verbose_name=_("Update"), orderable=False))])
        end_fields.append("update")
    else:
        # update links
        if not get_meta_class_value(model, "disable_create_update") is True:
            table_class.base_columns.update([("update", Column(accessor="get_update_link", verbose_name=_("Update"),
                                                           orderable=False))])
            end_fields.append("update")

    # clone link
    if get_meta_class_value(model, "cloneable") is True:
        table_class.base_columns.update([("clone", Column(accessor="get_clone_link", verbose_name=_("Clone"),
                                                          orderable=False))])
        end_fields.append("clone")
    # deletion links
    if get_meta_class_value(model, "allow_deletion"):
        table_class.base_columns.update([("delete", Column(accessor="get_delete_link", verbose_name=_("Delete"),
                                                           orderable=False))])
        end_fields.append("delete")

    # set column sequence
    table_class._meta.sequence = cleanup_fields(initial_fields, fields, additional_fields, end_fields)
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
