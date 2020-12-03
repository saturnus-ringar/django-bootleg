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
def get_alert(type, text):
    type = translate_django_type(type)
    if type not in ALERT_TYPES:
        raise ValueError("The type: %s is not a valid alert type" % type)
    return mark_safe('<div class="alert alert-%s mt-2" role="alert">%s</div>' % (type, text))


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
