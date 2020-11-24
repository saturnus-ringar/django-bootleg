from django.urls import reverse
from django.utils.safestring import mark_safe
import re

from django.utils.translation import ugettext as _


def strip_tags(html):
    return re.sub('<[^<]+?>', '', html)

def get_default_table_class_string():
    return "table table-striped table-responsive table-hover w-100 d-block d-md-table"


def get_nav_item(url, text):
    html = '<li class="nav-item dropdown">\n'
    html += '<li class="nav-item">\n'
    html += '<a class="nav-link" href="%s"></a>' % (url, text)
    html += '</li>\n'
    return mark_safe(html)


def display_in_menu(model):
    if not hasattr(model["meta"], "exclude_from_menu") and not model["meta"] is False:
        return True


def get_main_navigation(request):
    # circular imports ... :|
    from bootleg.templatetags.bootleg import get_changelist_url
    html = '<ul class="nav navbar-nav mr-auto float-left">'
    if request.user.is_staff and request.editable_models:
        html += '<li class="nav-item dropdown">\n'
        html += '<a class="nav-link dropdown-toggle" href="#" id="editable_models_list" data-toggle="dropdown"'
        html += ' aria-haspopup="true" aria-expanded="false">%s</a>\n' % _("List")
        html += '<div class="dropdown-menu" aria-labelledby="editable_models_list">\n'
        for model in request.editable_models:
            # dicts here - for the templates since they can't access _meta
            if display_in_menu(model):
                html += '<a class="dropdown-item" href="%s">%s</a>\n' % (
                reverse("bootleg:list_view", args=[model["meta"].model_name]),
                model["meta"].verbose_name_plural)
        html += '</div>'
        html += '</li>'

        html += '<li class="nav-item dropdown">\n'
        html += '<a class="nav-link dropdown-toggle" href="#" id="editable_models_create" data-toggle="dropdown"'
        html += ' aria-haspopup="true" aria-expanded="false">%s</a>\n' % _("Create")
        html += '<div class="dropdown-menu" aria-labelledby="editable_models_create">\n'
        for model in request.editable_models:
            if display_in_menu(model):
                # dicts here - for the templates since they can't access _meta
                html += '<a class="dropdown-item" href="%s">%s</a>\n' % (model["create_url"], model["meta"].verbose_name)
        html += '</div>'
        html += '</li>'

    if request.user.is_superuser:
        html += get_nav_item(reverse("bootleg:system_info"), _("System"))
        html += get_nav_item(reverse("bootleg:deploy_info"), _("Deployment"))
        html += get_nav_item(get_changelist_url('bootleg', 'LoggedException') + "?handled__exact=0",
            _("Logged exceptions"), request.unhandled_logged_exceptions_count, True)
        html += get_nav_item(get_changelist_url('bootleg', 'DjangoLogEntry') + "?handled__exact=0",
            _("Django log entries"), request.unhandled_django_log_entry_count, True)
        html += get_nav_item(get_changelist_url('bootleg', 'JavascriptError') + "?handled__exact=0",
            _("Javascript errors"), request.unhandled_javascript_error_count, True)

    html += "</ul>"
    return mark_safe(html)


def get_right_navigation(request):
    html = '<ul class="nav navbar-nav navbar-right">\n'

    if not request.user.is_authenticated:
        html += get_nav_item(reverse("bootleg:login"), _("Login"))

    if request.user.is_authenticated:
        html += '<li class="nav-item dropdown float-right">\n'
        html += '<a class ="nav-link dropdown-toggle" href="#" id="profile_dropdown" data-toggle="dropdown"'
        html += ' aria-haspopup="true" aria-expanded="false">%s</a>\n' % request.user.username
        html += '<div class="dropdown-menu dropdown-menu-right" aria-labelledby="profile_dropdown">\n'
        html += '<a class ="dropdown-item" href="%s">%s</a>\n' % (reverse("bootleg:change_password"), _("Change password"))
        html += '<a class ="dropdown-item" href="%s">%s</a>\n' % (reverse("bootleg:logout"), _("Log out"))

    if request.user.is_staff:
        html += '<a class ="dropdown-item" href="%s">%s</a>\n' % (reverse("admin:index"), _("Django-admin"))

    html += '</div>\n'
    html += '</li>\n'
    html += '</ul>\n'
    return html


def get_nav_item(url, text, count=None, target_blank=False):
    target = ''
    if target_blank:
        target = ' target="_blank" '
    html = '<li class ="nav-item">\n'
    html += '<a class="nav-link" href="%s"%s>%s\n' % (url, target, text)
    if count:
        html += '<span class ="badge badge-pill badge-danger navbar-badge">%s</span>' \
                % count
    html += '</a>\n'
    return html
