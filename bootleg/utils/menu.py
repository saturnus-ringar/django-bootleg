from django.urls import reverse
from django.utils.safestring import mark_safe

from bootleg.conf import bootleg_settings
from django.utils.translation import ugettext as _

############################################
# dropdowns
############################################
from bootleg.logging.logging import log_exception
from bootleg.utils.models import display_model_in_menu


def get_dropdown_head(id, title, css_class=None):
    clazz = ""
    if css_class:
        clazz = " %s" % css_class
    html = '<li class="nav-item dropdown%s">\n' % clazz
    html += '<a class ="nav-link dropdown-toggle" href="#" id="profile_dropdown" data-toggle="%s"' % id
    html += ' aria-haspopup="true" aria-expanded="false">%s</a>\n' % title
    html += '<div class="dropdown-menu dropdown-menu-right" aria-labelledby="%s">\n' % id
    return mark_safe(html)


def get_dropdown_foot():
    html = '</div>\n'
    html += '</li>\n'
    return html


def get_dropdown_item(url, text):
    return mark_safe('<a class ="dropdown-item" href="%s">%s</a>\n' % (url, text))


def get_nav_item(url, text, dropdown=False, count=None, target_blank=False):
    css_class = ""
    if dropdown:
        css_class = " dropdown"
    target = ''
    if target_blank:
        target = ' target="_blank" '
    html = '<li class="nav-item%s">\n' % css_class
    html += '<a class="nav-link" href="%s"%s>%s\n' % (url, target, text)
    if count:
        html += '<sup><span class="badge badge-pill badge-danger progress-bar-danger">%s</span></sup>' % count
    html += '</li>\n'
    html += '</a>\n'
    return mark_safe(html)


def get_right_dropdown(request):
    html = ''
    if request.user.is_authenticated:
        html += '<ul class="nav navbar-nav navbar-right">\n'
        html += get_dropdown_head("profile_dropdown", request.user.username, "float-right")
        html += get_dropdown_item(reverse("bootleg:change_password"), _("Change password"))
        html += get_dropdown_item(reverse("bootleg:logout"), _("Log out"))
        if request.user.is_staff:
            html += get_dropdown_item(reverse("admin:index"), _("Django-admin"))
        html += get_dropdown_foot()
    return mark_safe(html)


def get_models_dropdown(request, create=False):
    output = False
    if create:
        html = get_dropdown_head("models_create", _("Create"))
    else:
        html = get_dropdown_head("models_list", _("List"))

    for model in request.editable_models:
        if display_model_in_menu(model, request, create=create):
            if create:
                html += get_dropdown_item(model["class"].get_create_url(), model["meta"].verbose_name_plural)
            else:
                html += get_dropdown_item(model["class"].get_list_url(), model["meta"].verbose_name_plural)
            output = True

    if not output:
        html = ""
    else:
        html += get_dropdown_foot()
    return mark_safe(html)


def get_main_navigation(request):
    # the models are dicts here, for template usage
    if request.editable_models:
        html = '<ul class="nav navbar-nav mr-auto float-left">\n'
        if bootleg_settings.EDITABLE_IN_DROPDOWN:
            html += get_models_dropdown(request, create=False)
        else:
            # not in dropdowns
            for model in request.editable_models:
                if display_model_in_menu(model, request):
                    html += get_nav_item(model["class"].get_list_url(), model["meta"].verbose_name_plural)
        html += get_models_dropdown(request, create=True)
        html += '</ul>'
    html += get_right_navigation(request)
    return mark_safe(html)


def get_right_navigation(request):
    from bootleg.templatetags.bootleg import get_changelist_url
    html = '<ul class="nav navbar-nav navbar-right">\n'
    if request.user.is_superuser:
        html += get_nav_item(get_changelist_url('bootleg', 'LoggedException') + "?handled__exact=0",
            _("Logged exceptions"), count=request.unhandled_logged_exceptions_count, target_blank=True)
        html += get_nav_item(get_changelist_url('bootleg', 'DjangoLogEntry') + "?handled__exact=0",
            _("Log entries"), count=request.unhandled_django_log_entry_count, target_blank=True)
        html += get_nav_item(get_changelist_url('bootleg', 'JavascriptError') + "?handled__exact=0",
            _("JS-errors"), count=request.unhandled_javascript_error_count, target_blank=True)
        html += get_dropdown_head("superuser_tools", _("Tools"), css_class="float-right")
        html += get_dropdown_item(reverse("bootleg:system_info"), _("System"))
        html += get_dropdown_item(reverse("bootleg:deploy_info"), _("Deployment"))
        html += get_dropdown_item(reverse("bootleg:models_info"), _("Models"))
        html += get_dropdown_item(reverse("bootleg:debug"), _("Debug"))
        html += get_dropdown_foot()

    if not request.user.is_authenticated:
        html += get_nav_item(reverse("bootleg:login"), _("Login"))
    else:
        html += get_right_dropdown(request)
    html += '</ul>'
    return mark_safe(html)
