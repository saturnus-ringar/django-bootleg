from bootleg.utils import html as bootleg_html
from django import template
from django.apps import apps
from django.urls import reverse
from django.utils.safestring import mark_safe

from bootleg.utils import strings
from bootleg.utils.humanize import humanize_bytes as hb
from django.utils.translation import ugettext as _

register = template.Library()


@register.simple_tag
def get_changelist_url(app, model):
    return apps.get_model(app_label=app, model_name=model).get_changelist_url()


@register.filter
def nl2br(string):
    return strings.nl2br(string)


@register.filter
def humanize_bytes(value):
    if isinstance(value, int):
        return hb(value)
    else:
        return value


@register.simple_tag
def render_navigation(request):
    html = bootleg_html.get_main_navigation(request)
    html += bootleg_html.get_right_navigation(request)
    return mark_safe(html)


@register.simple_tag
def get_first_with_value(*args):
    for arg in args:
        if arg:
            return arg

    return ""
