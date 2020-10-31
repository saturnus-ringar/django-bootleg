import logging
import os

from django.template import TemplateDoesNotExist
from django.template.loader import get_template

from bootleg.system import file_system, nix
from django.apps import AppConfig
from django.core.checks import Error, register
from giturlparse import validate

from bootleg.utils import models
from bootleg.conf import bootleg_settings
from django.conf import settings


def check_django_log_level(errors):
    level = bootleg_settings.DJANGO_LOG_LEVEL
    if level in ["CRITICAL", "FATAL", "NOTSET"]:
        errors.append(
            Error(
                'DJANGO_LOG_LEVEL %s is not allowed' % level,
                hint='Valid levels are: DEBUG, WARNING, ERROR',
                obj=bootleg_settings,
                id='bootleg.E001',
            )
        )

    try:
        logging._checkLevel(level)
    except ValueError:
        errors.append(
            Error(
                'DJANGO_LOG_LEVEL %s is not a valid level' % level,
                hint='Valid levels are: DEBUG, WARNING, ERROR',
                obj=bootleg_settings,
                id='bootleg.E001',
            )
        )

    return errors


def check_sql_logging(errors):
    if bootleg_settings.LOG_SQL and not bootleg_settings.DEBUG:
        errors.append(
            Error(
                "LOG_SQL is set to True but DEBUG is False; the SQL won't be logged if DEBUG is False",
                hint='Set DEBUG to True and LOG_SQL to True',
                obj=bootleg_settings,
                id='bootleg.E002',
            )
        )

    return errors


def check_log_dir(errors):
    dir = bootleg_settings.LOG_DIR
    if not file_system.is_writable(dir):
        errors.append(
            Error(
                "LOG_DIR %s is not writable" % dir,
                hint='chmod and or create %s' % dir,
                obj=bootleg_settings,
                id='bootleg.E003',
            )
        )

    return errors


def check_site_domain(errors):
    if not bootleg_settings.SITE_DOMAIN:
        errors.append(
            Error(
                "SITE_DOMAIN is not in the settings",
                hint="Set SITE_DOMAIN to the site's domain name",
                obj=bootleg_settings,
                id='bootleg.E004',
            )
        )

    return errors


def check_site_name(errors):
    if not bootleg_settings.SITE_NAME:
        errors.append(
            Error(
                "SITE_NAME is not in the settings",
                hint="Set SITE_NAME to the site's name",
                obj=bootleg_settings,
                id='bootleg.E005',
            )
        )

    return errors


def check_home_url(errors):
    # currently this will raise a ConfigurationError:
    # "bootleg.conf.settings.ConfigurationError: HOME_URL must be defined in settings."
    # ... but I'm keeping this check. For now.
    if not bootleg_settings.HOME_URL:
        errors.append(
            Error(
                "HOME_URL is not in the settings",
                hint="Set HOME_URL to a valid URL",
                obj=bootleg_settings,
                id='bootleg.E006',
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
    if template or required:
        try:
            get_template(template)
        except TemplateDoesNotExist:
            errors.append(
                Error(
                    "Could not find template: %s" % template,
                    hint="Set %s to a valid file." % attribute,
                    obj=settings,
                    id='bootleg.%s' % number
                )
            )

    return errors


@register()
def check_settings(app_configs, **kwargs):
    '''
    errors = check_django_log_level([])
    errors = check_sql_logging(errors)
    errors = check_log_dir(errors)
    errors = check_site_domain(errors)
    errors = check_site_name(errors)
    errors = check_home_url(errors)
    if not settings.DEBUG:
        # only check users and groups if we're live
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
    errors = check_template(errors, "NAVIGATION_TEMPLATE", bootleg_settings.NAVIGATION_TEMPLATE, 17)
    errors = check_template(errors, "SYSTEM_TEMPLATE", bootleg_settings.SYSTEM_TEMPLATE), 18)
    errors = check_template(errors, "DEPLOYMENT_TEMPLATE", bootleg_settings.DEPLOYMENT_TEMPLATE, 19)
    errors = check_template(errors, "ERROR_400_TEMPLATE", bootleg_settings.ERROR_400_TEMPLATE, 20)
    errors = check_template(errors, "ERROR_403_TEMPLATE", bootleg_settings.ERROR_403_TEMPLATE, 21)
    errors = check_template(errors, "ERROR_404_TEMPLATE", bootleg_settings.ERROR_404_TEMPLATE, 22)
    errors = check_template(errors, "ERROR_500_TEMPLATE", bootleg_settings.ERROR_500_TEMPLATE, 22)
    '''
    # check files
    errors = []
    return errors


class BootlegConfig(AppConfig):
    name = 'bootleg'

    def ready(self):
        models.setup_default_site()
