from bootleg import utils
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
    return strings.snl2br(string)


@register.filter
def humanize_bytes(value):
    if isinstance(value, int):
        return hb(value)
    else:
        return value


@register.simple_tag
def render_navigation(request):
    html = ''
    if request.user.is_staff:
        html = utils.html.get_nav_item(get_changelist_url('bootleg', 'LoggedException') + "?handled__exact=0",
                                       _("Logged exceptions"),
                                       request.unhandled_logged_exceptions_count, True)
        html += utils.html.get_nav_item(get_changelist_url('bootleg', 'DjangoLogEntry') + "?handled__exact=0",
                                        _("Django log entries"),
                                       request.unhandled_django_log_entry_count, True)

    if request.editable_models:
        html += '<li class ="nav-item dropdown">\n'
        html += '<a class ="nav-link dropdown-toggle" href="#" id="editable_models_list" data-toggle="dropdown"'
        html += ' aria-haspopup="true" aria-expanded="false">%s</a>\n' % _("List")
        html += '<div class="dropdown-menu" aria-labelledby="editable_models_list">\n'

        for model in request.editable_models:
            # "meta" is a dict here - for the templates since they can't access _meta
            html += '<a class="dropdown-item" href="%s">%s</a>\n' % (reverse("list_view", args=[model["meta"].model_name]),
                                                                    model["meta"].verbose_name_plural)
            html += '</div>\n'
        html += '</li>\n'

        html += '<li class="nav-item dropdown">\n'
        html += '<a class="nav-link dropdown-toggle" href="#" id="editable_models_create" data-toggle="dropdown"'
        html += ' aria-haspopup="true" aria-expanded="false">%s</a>\n' % _("Create")
        html += '<div class="dropdown-menu" aria-labelledby="editable_models_create">\n'
        for model in request.editable_models:
            # dicts here - for the templates since they can't access _meta
            html += '<a class="dropdown-item" href="%s">%s</a>\n' % (model["create_url"], model["meta"].verbose_name)
        html += '</div>'
        html += '</li>'

    return mark_safe(html)


@register.simple_tag
def render_right_navigation(request):
    html = ''
    if request.user.is_authenticated:
        html += '<ul class="nav navbar-nav navbar-right">\n'
        html += '<li class="nav-item dropdown float-right">\n'
        html += '<a class ="nav-link dropdown-toggle" href="#" id="profile_dropdown" data-toggle="dropdown"'
        html += ' aria-haspopup="true" aria-expanded="false">%s</a>\n' % request.user.username
        html += '<div class="dropdown-menu dropdown-menu-right" aria-labelledby="profile_dropdown">\n'
        html += '<a class ="dropdown-item" href="%s">%s</a>\n' % (reverse("change_password"), _("Change password"))
        html += '<a class ="dropdown-item" href="%s">%s</a>\n' % (reverse("logout"), _("Log out"))

    if request.user.is_staff:
        html += '<a class ="dropdown-item" href="%s">%s</a>\n' % (reverse("admin:index"), _("Django-admin"))

    html += '</div>\n'
    html += '</li>\n'
    html += '</ul>\n'

    return mark_safe(html)


@register.simple_tag
def get_first_with_value(*args):
    for arg in args:
        if arg:
            return arg

    return ""
