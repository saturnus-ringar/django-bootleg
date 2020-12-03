from django.apps import AppConfig
from django.conf import settings
from django.contrib.staticfiles import finders
from django.core.checks import Error, Warning, register
from django.template import TemplateDoesNotExist
from django.template.loader import get_template
from django.urls import reverse, NoReverseMatch

from bootleg.conf import bootleg_settings
from bootleg.conf.settings import ConfigurationError, DEFAULT_FAVICON
from bootleg.system import nix
from bootleg.system.nix import setup_alias_file
from bootleg.utils import models, env


def check_sql_logging(errors):
    if bootleg_settings.LOG_SQL and not settings.DEBUG:
        errors.append(
            Error(
                "LOG_SQL is set to True but DEBUG is False; the SQL won't be logged if DEBUG is False",
                hint='Set DEBUG to True and LOG_SQL to True',
                obj=bootleg_settings,
                id='bootleg.E002',
            )
        )

    return errors


def check_required_setting(errors, attribute, number):
    if not getattr(bootleg_settings, attribute, None):
        errors.append(
            Error(
                "%s is not in the settings" % attribute,
                hint="Add %s to the settings" % attribute,
                obj=bootleg_settings,
                id='bootleg.E00%' % number
            )
        )

    return errors


def check_user(errors, username, setting, number):
    if not nix.user_exists(username):
        errors.append(
            Error(
                "User: %s doesn't exist" % username,
                hint='Set an existing user in %s' % setting,
                obj=settings,
                id='bootleg.E00%s' % number
            )
        )

    return errors


def check_group(errors, group, setting, number):
    if not nix.group_exists(group):
        errors.append(
            Error(
                "Group: %s doesn't exist" % group,
                hint='Set an existing group in %s' % setting,
                obj=settings,
                id='bootleg.E00%s' % number
            )
        )

    return errors


def check_user_is_in_group(errors, user, group, number):
    if not nix.user_is_in_group(user, group):
        errors.append(
            Error(
                "User: %s is not in group: %s" % (user, group),
                hint='Add the user: %s in group: %s' % (user, group),
                obj=settings,
                id='bootleg.E00%s' % number
            )
        )

    return errors


def check_template(errors, attribute, template, number, required=False):
    if required and not template:
        errors.append(
            Error(
                "Template %s must be set in the settings" % attribute,
                hint="Add %s to the settings" % attribute,
                obj=settings,
                id='bootleg.%s' % number
            )
        )
        return errors

    if template or required:
        try:
            get_template(template)
        except TemplateDoesNotExist:
            errors.append(
                Error(
                    "Could not find template: %s" % template,
                    hint="Set %s to a valid file" % attribute,
                    obj=settings,
                    id='bootleg.%s' % number
                )
            )

    return errors


def check_boolean(errors, attribute, number):
    value = getattr(settings, attribute, None)
    if value and not isinstance(value, bool):
        errors.append(
            Error(
                "%s must be a boolean value" % attribute,
                hint="Set %s to a boolean value file" % attribute,
                obj=settings,
                id='bootleg.EO%s' % number
            )
        )

    return errors


def check_css_files(errors):
    if not isinstance(bootleg_settings.CSS_FILES, list):
        errors.append(
            Error(
                "CSS_FILES must be a list",
                hint="Set CSS_FILES to a list",
                obj=settings,
                id="bootleg.EO28"
            )
        )
    else:
        # it's a list containing entries, verify that the files exist
        for css_file in bootleg_settings.CSS_FILES:
            if not finders.find(css_file):
                errors.append(
                    Error(
                        "Could not find the css file: %s from CSS_FILES" % css_file,
                        hint="Add an existing file",
                        obj=settings,
                        id="bootleg.E029"
                    )
                )

    return errors


def check_login_redirect_url(errors):
    if settings.LOGIN_REDIRECT_URL == '/accounts/profile/':
        errors.append(
            Error(
                "LOGIN_REDIRECT_URL has Django's default value",
                hint="Set LOGIN_REDIRECT_URL to an URL (as a string) that will be reversed",
                obj=settings,
                id="bootleg.E028"
            )
        )
    else:
        # not the default URL
        try:
            reverse(settings.LOGIN_REDIRECT_URL)
        except NoReverseMatch:
            errors.append(
                Error(
                    "LOGIN_REDIRECT_URL %s could not be reversed" % settings.LOGIN_REDIRECT_URL,
                    hint="Set LOGIN_REDIRECT_URL to a valid url name",
                    obj=settings,
                    id="bootleg.E029"
                )
            )

    return errors


def check_favicon(errors):
    if bootleg_settings.FAVICON_FILE == DEFAULT_FAVICON:
        errors.append(
            Warning(
                "FAVICON_FILE has not been set. Bootleg's default favicon is used",
                hint="Set FAVICON_FILE in settings to a file",
                obj=settings,
                id="bootleg.E029"
            )
        )
    else:
        # not the default favicon
        if not finders.find(bootleg_settings.FAVICON_FILE):
            errors.append(
                Error(
                    "Could not find the favicon file: %s" % bootleg_settings.FAVICON_FILE,
                    hint="Set FAVICON_FILE to an existing file",
                    obj=settings,
                    id="bootleg.E029"
                )
            )

    return errors


def check_profile_model(errors):
    if getattr(settings, "PROFILE_MODEL", None):
        try:
            models.get_profile_model()
            if not models.is_valid_profile_model():
                errors.append(
                    Error(
                        "The PROFILE_MODEL: %s is not a valid profile model" % settings.PROFILE_MODEL,
                        hint="Extend bootleg.Profile in your profile model",
                        obj=settings,
                        id="bootleg.E030"
                    )
                )
        except Exception:
            errors.append(
                Error(
                    "Could not find the PROFILE_MODEL: %s" % settings.PROFILE_MODEL,
                    hint="Set PROFILE_MODEL to an existing model: app_name.ModelName",
                    obj=settings,
                    id="bootleg.E031"
                )
            )

    return errors


@register()
def check_settings(app_configs, **kwargs):
    errors = []
    errors = check_required_setting(errors, "SITE_DOMAIN", 4)
    errors = check_required_setting(errors, "SITE_DOMAIN", 4)
    errors = check_required_setting(errors, "SITE_NAME", 4)
    errors = check_required_setting(errors, "HOME_URL", 4)
    errors = check_required_setting(errors, "HOME_URL", 4)

    if env.is_production():
        # only check users and groups if it's in production
        errors = check_user(errors, bootleg_settings.MAIN_USER, "MAIN_USER", 7)
        errors = check_user(errors, bootleg_settings.WEBSERVER_USER, "WEBSERVER_USER", 8)
        errors = check_group(errors, bootleg_settings.MAIN_USER_GROUP, "MAIN_USER_GROUP", 9)
        errors = check_group(errors, bootleg_settings.WEBSERVER_USER_GROUP, "WEBSERVER_USER_GROUP", 10)
        errors = check_user_is_in_group(errors, bootleg_settings.MAIN_USER, bootleg_settings.MAIN_USER_GROUP, 11)
        errors = check_user_is_in_group(errors, bootleg_settings.WEBSERVER_USER, bootleg_settings.WEBSERVER_USER_GROUP, 12)
        errors = check_user_is_in_group(errors, bootleg_settings.MAIN_USER, bootleg_settings.WEBSERVER_USER_GROUP, 13)
        errors = check_user_is_in_group(errors, bootleg_settings.WEBSERVER_USER, bootleg_settings.MAIN_USER_GROUP, 14)

    # check templates
    errors = check_template(errors, "BASE_TEMPLATE", bootleg_settings.BASE_TEMPLATE, 16, required=True)
    errors = check_template(errors, "NAVIGATION_TEMPLATE", bootleg_settings.NAVIGATION_TEMPLATE, 17, required=True)
    errors = check_template(errors, "SYSTEM_TEMPLATE", bootleg_settings.SYSTEM_TEMPLATE, 18)
    errors = check_template(errors, "DEPLOYMENT_TEMPLATE", bootleg_settings.DEPLOYMENT_TEMPLATE, 19)
    errors = check_template(errors, "ERROR_400_TEMPLATE", bootleg_settings.ERROR_400_TEMPLATE, 20, required=True)
    errors = check_template(errors, "ERROR_403_TEMPLATE", bootleg_settings.ERROR_403_TEMPLATE, 21, required=True)
    errors = check_template(errors, "ERROR_404_TEMPLATE", bootleg_settings.ERROR_404_TEMPLATE, 22, required=True)
    errors = check_template(errors, "ERROR_500_TEMPLATE", bootleg_settings.ERROR_500_TEMPLATE, 22, required=True)
    errors = check_boolean(errors, "ADD_BUILTINS", 23)
    errors = check_boolean(errors, "LOG_SQL", 24)
    errors = check_boolean(errors, "LOG_TO_STDOUT", 25)
    errors = check_boolean(errors, "PRINT_AT_STARTUP", 26)
    errors = check_boolean(errors, "STORE_DJANGO_LOG_EXCEPTIONS", 27)
    errors = check_boolean(errors, "STORE_LOGGED_EXCEPTIONS", 28)
    errors = check_css_files(errors)
    errors = check_login_redirect_url(errors)
    errors = check_favicon(errors)
    errors = check_profile_model(errors)

    return errors


class BootlegConfig(AppConfig):
    name = 'bootleg'

    def ready(self):
        if not getattr(settings, "BOOTLEG_SETTINGS_IMPORTED", None):
            raise ConfigurationError("The bootleg settings have not been imported. Add this (as the last line) "
                                     "to settings.py: from bootleg.settings import *")
        models.setup_default_site()
        if env.is_manage():
            setup_alias_file()
