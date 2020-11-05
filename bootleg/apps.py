from django.apps import AppConfig
from django.conf import settings
from django.core.checks import Error, register
from django.template import TemplateDoesNotExist
from django.template.loader import get_template
from giturlparse import validate

from bootleg.conf import bootleg_settings
from bootleg.conf.settings import ConfigurationError
from bootleg.system import nix
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


def check_git_url(errors):
    git_url = bootleg_settings.GIT_URL
    if git_url and not validate(git_url):
        errors.append(
            Error(
                "GIT_URL: %s is not a valid github-repo-URL" % git_url,
                hint='Set a valid github-repo-URL in GIT_URL in the settings',
                obj=settings,
                id='bootleg.E015'
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
                hint="Set %s to a boolean value file." % attribute,
                obj=settings,
                id='bootleg.%s' % number
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
        errors = check_git_url(errors)

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
    errors = check_boolean(errors, "LOG_TO_STDOUT", 23)
    errors = check_boolean(errors, "PRINT_AT_STARTUP", 23)
    errors = check_boolean(errors, "STORE_DJANGO_LOG_EXCEPTIONS", 23)
    errors = check_boolean(errors, "STORE_LOGGED_EXCEPTIONS", 23)

    return errors


class BootlegConfig(AppConfig):
    name = 'bootleg'

    def ready(self):
        if not getattr(settings, "BOOTLEG_SETTINGS_IMPORTED", None):
            raise ConfigurationError("The bootleg settings have not been imported. Add this (as the last line) "
                                     "to settings.py: from bootleg.settings import *")
        models.setup_default_site()
