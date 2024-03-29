from bootleg.system.commands import SAR_COMMAND_EXISTS
from django import template
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _
from bootleg.utils import html

register = template.Library()

ALERT_TYPES = ["primary", "secondary", "success", "danger", "warning", "info", "light", "dark"]


def translate_django_type(type):
    if type == "error":
        type = "danger"
    elif type == "debug":
        type = "primary"

    return type


@register.simple_tag
def get_button(text, id=None):
    id_output = ""
    if id:
        id_output = ' id="%s"' % id

    return mark_safe('<input type="submit" name="submit" value="%s" '
                     'class="btn btn-primary loading-button mb-2"%s>' % (text, id_output))


@register.simple_tag
def get_alert(type, text, dismissable=False):
    type = translate_django_type(type)
    dismiss_class = ""
    if dismissable:
        dismiss_class = " alert-dismissible"
    if type not in ALERT_TYPES:
        raise ValueError("The type: %s is not a valid alert type" % type)
    html = '<div class="alert alert-%s mt-2%s" role="alert"><strong>%s</strong>\n' % (type, dismiss_class, text)
    if dismissable:
        html += '<button type="button" class="close" data-dismiss="alert" aria-label="Close">\n'
        html += '<span aria-hidden="true">&times;</span>\n'
        html += '</button>\n'
    html += '</div>\n'
    return mark_safe(html)


@register.simple_tag
def get_card_top():
    html = '<div class="card">'
    html += '<div class="card-body">'
    return mark_safe(html)


@register.simple_tag
def get_card_bottom():
    html = '</div>'
    html += '</div>'
    return mark_safe(html)


@register.simple_tag
def get_default_table_classes():
    return html.get_default_table_class_string()


@register.simple_tag
def sar_warning():
    if not SAR_COMMAND_EXISTS:
        return get_alert("warning", _("The SAR command doesn't exist on this system. This is not real data."))
    return ""


@register.simple_tag
def render_search_append(id=None):
    id_out = "main_search_button"
    if id:
        id_out = id
    html = '<div class="input-group-append">\n'
    html += '<button class="btn btn-secondary" id="%s" type="button">\n' % id_out
    html += '<i class="fa fa-search"></i>\n'
    html += '</button>'
    html += '</div>'
    return mark_safe(html)
