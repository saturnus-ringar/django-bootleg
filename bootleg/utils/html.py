from django.urls import reverse
from django.utils.safestring import mark_safe
import re

from django.utils.translation import ugettext as _
from bootleg.conf import bootleg_settings
from bootleg.utils.utils import meta_class_value_is_true


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


def display_in_menu(model, create=False):
    if create and getattr(model["meta"], "disable_create_update", None) is not True:
        return False

    if not getattr(model["meta"], "exclude_from_menu", None) is True:
        return True


def display_model(request, model):
    if request.user.is_staff or getattr(model["meta"], "public_listing", None) is True:
        return True

    return False


def get_main_navigation(request):
    html = '<ul class="nav navbar-nav mr-auto float-left">'
    if request.editable_models:
        list_output = False
        list_html = ""
        if bootleg_settings.EDITABLE_IN_DROPDOWN:
            list_html = '<li class="nav-item dropdown">\n'
            list_html += '<a class="nav-link dropdown-toggle" href="#" id="editable_models_list" data-toggle="dropdown"'
            list_html += ' aria-haspopup="true" aria-expanded="false">%s</a>\n' % _("List")
            list_html += '<div class="dropdown-menu" aria-labelledby="editable_models_list">\n'

        for model in request.editable_models:
            dx(model)
            if display_model(request, model):
                if not bootleg_settings.EDITABLE_IN_DROPDOWN:
                    # no dropdown, indeed
                    list_html += '<li class="nav-item">'
                # dicts here - for the templates since they can't access _meta
                if display_in_menu(model):
                    css_class = "dropdown-item"
                    if not bootleg_settings.EDITABLE_IN_DROPDOWN:
                        css_class = "nav-link"
                    list_html += '<a class="%s" href="%s">%s</a>\n' % (css_class,
                    reverse("bootleg:list_view", args=[model["meta"].model_name]),
                    model["meta"].verbose_name_plural)
                    list_output = True
                if not bootleg_settings.EDITABLE_IN_DROPDOWN:
                    list_html += '</li>'

            if bootleg_settings.EDITABLE_IN_DROPDOWN:
                list_html += '</div>'
                list_html += '</li>'

            if not list_output:
                list_html = ""

        html += list_html

    if request.user.is_staff:
        create_output = False
        create_html = '<li class="nav-item dropdown">\n'
        create_html += '<a class="nav-link dropdown-toggle" href="#" id="editable_models_create" data-toggle="dropdown"'
        create_html += ' aria-haspopup="true" aria-expanded="false">%s</a>\n' % _("Create")
        create_html += '<div class="dropdown-menu" aria-labelledby="editable_models_create">\n'
        for model in request.editable_models:
            if display_in_menu(model, create=True):
                # dicts here - for the templates since they can't access _meta
                create_html += '<a class="dropdown-item" href="%s">%s</a>\n' % (model["create_url"], model["meta"].verbose_name)
                create_output = True
        create_html += '</div>'
        create_html += '</li>'

        if not create_output:
            create_html = ""

        html += create_html

    html += "</ul>"
    return mark_safe(html)


def get_dropdown_header(id, title):
    html = '<li class="nav-item dropdown float-right">\n'
    html += '<a class ="nav-link dropdown-toggle" href="#" id="profile_dropdown" data-toggle="%s"' % id
    html += ' aria-haspopup="true" aria-expanded="false">%s</a>\n' % title
    html += '<div class="dropdown-menu dropdown-menu-right" aria-labelledby="%s">\n' %id
    return mark_safe(html)


def get_dropdown_item(url, text):
    return mark_safe('<a class ="dropdown-item" href="%s">%s</a>\n' % (url, text))


def get_right_navigation(request):
    # circular imports ... :|
    from bootleg.templatetags.bootleg import get_changelist_url
    html = '<ul class="nav navbar-nav navbar-right">\n'

    if request.user.is_superuser:
        html += get_nav_item(get_changelist_url('bootleg', 'LoggedException') + "?handled__exact=0",
            _("Logged exceptions"), request.unhandled_logged_exceptions_count, True)
        html += get_nav_item(get_changelist_url('bootleg', 'DjangoLogEntry') + "?handled__exact=0",
            _("Log entries"), request.unhandled_django_log_entry_count, True)
        html += get_nav_item(get_changelist_url('bootleg', 'JavascriptError') + "?handled__exact=0",
            _("JS-errors"), request.unhandled_javascript_error_count, True)

        dropdown_name = "superuser_tools"
        html += get_dropdown_header(dropdown_name, _("Tools"))
        html += get_dropdown_item(reverse("bootleg:system_info"), _("System"))
        html += get_dropdown_item(reverse("bootleg:deploy_info"), _("Deployment"))
        html += get_dropdown_item(reverse("bootleg:models_info"), _("Models"))

    if not request.user.is_authenticated:
        html += get_nav_item(reverse("bootleg:login"), _("Login"))

    if request.user.is_authenticated:
        dropdown_id = "profile_dropdown"
        html += get_dropdown_header(dropdown_id, request.user.username)
        html += get_dropdown_item(reverse("bootleg:change_password"), _("Change password"))
        html += get_dropdown_item(reverse("bootleg:logout"), _("Log out"))

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
        html += '<sup><span class="badge badge-pill badge-danger progress-bar-danger">%s</span></sup>' % count
    html += '</a>\n'
    return html
