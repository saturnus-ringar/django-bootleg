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

from bootleg.conf import bootleg_settings
from bootleg.system.git import GitData
from bootleg.system.system import System
from bootleg.utils import strings
from bootleg.utils.humanize import humanize_bytes as hb
from bootleg.utils.menu import get_right_navigation, get_main_navigation
from bootleg.utils.utils import get_meta_class_value

register = template.Library()

BLANK_VALUE = "-"


@register.simple_tag
def debug_bl(string):
    if bootleg_settings.BOOTLEG_DEBUG:
        return mark_safe('<div class="text-muted"><small>%s</small></div>' % string)
    else:
        return ""


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
    html = get_main_navigation(request)
    #html += get_right_navigation(request)
    return mark_safe(html)


@register.simple_tag()
def render_main_navigation(request):
    return mark_safe(get_main_navigation(request))


@register.simple_tag
def render_right_navigation(request):
    return mark_safe(get_right_navigation(request))


@register.simple_tag
def get_page_title(model, page_title_1, page_title_2):
    title = get_first_with_value(*[page_title_1, page_title_2])
    if not title:
        title = bootleg_settings.SITE_NAME
        if model:
            title += " - " + model["meta"].verbose_name_plural

    return title


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

    if value is None:
        value = "-"

    return value


@register.simple_tag()
def get_many_to_many_fields_values(obj, attribute):
    return getattr(obj, attribute).all()


@register.simple_tag()
def get_class(obj):
    return obj.__class__.__name__


@register.simple_tag()
def render_many_to_one_objects(obj):
    html = ""
    objects_data = obj.get_many_to_one_objects()
    for key in objects_data.keys():
        has_objects = False
        object_html = ""
        object_html += '<h4 class="mt-4">%s</h4>\n' % key
        object_html += '<ul class="list-unstyled">'
        for many_to_one_obj in objects_data[key]["objects"]:
            object_html += '<li>%s</li>' % str(many_to_one_obj) + '\n'
            has_objects = True
        if not has_objects:
            object_html = ""
        else:
            object_html += '</ul>'

        html += object_html

    return mark_safe(html)


@register.simple_tag()
def render_value(value):
    if not value:
        return BLANK_VALUE
    return value


@register.simple_tag()
def render_model_meta_value(model, attr):
    value = get_meta_class_value(model, attr)
    if not value:
        return BLANK_VALUE

    return value
