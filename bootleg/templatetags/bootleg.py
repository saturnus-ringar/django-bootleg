import datetime

from django import template
from django.apps import apps
from django.conf import settings
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.db.models.fields.files import ImageFieldFile
from django.template.loader import render_to_string
from django.utils import formats
from django.utils.formats import date_format
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _

from bootleg.system.git import GitData
from bootleg.system.system import System
from bootleg.utils import html as bootleg_html
from bootleg.utils import strings
from bootleg.utils.humanize import humanize_bytes as hb

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


@register.simple_tag()
def render_main_navigation(request):
    return mark_safe(bootleg_html.get_main_navigation(request))


@register.simple_tag
def render_right_navigation(request):
    return mark_safe(bootleg_html.get_right_navigation(request))


@register.simple_tag
def get_first_with_value(*args):
    for arg in args:
        if arg:
            return arg

    return ""


@register.simple_tag
def render_last_modified_file(file):
    html = ""
    if file:
        html = '<br /><small>%s' % _("Modified")
        html += ' %s (%s)</small>' \
                % ((formats.date_format(file["date"], "DATETIME_FORMAT"), naturaltime(file["date"])))
        html += '<br /><small class="text-muted">%s</span></p>' % file["path"]

    return mark_safe(html)


@register.simple_tag
def render_system_info():
    return render_to_string("bootleg/includes/system_info.html", {"system": System()})


@register.simple_tag
def render_deploy_info():
    return render_to_string("bootleg/includes/deploy_info.html", {"git_data": GitData()})


@register.simple_tag()
def get_attribute(obj, attribute):
    value = getattr(obj, attribute)
    if isinstance(value, datetime.date):
        # format dates
        try:
            return date_format(value, getattr(settings, "DATETIME_FORMAT"))
        except TypeError:
            return date_format(value, getattr(settings, "DATE_FORMAT"))

    if isinstance(value, ImageFieldFile):
        return value.url

    return value


@register.simple_tag()
def get_many_to_many_fields_values(obj, attribute):
    return getattr(obj, attribute).all()


@register.simple_tag()
def get_class(obj):
    return obj.__class__.__name__
