from django.apps import AppConfig
from django.core.checks import Error, register

from bootleg.utils import models, file_system
from bootleg.conf import settings


def check_home_url(errors):
    # currently this will raise a ConfigurationError:
    # "bootleg.conf.settings.ConfigurationError: HOME_URL must be defined in settings."
    # ... but I'm keeping this check. For now.
    if not settings.home_url():
        errors.append(
            Error(
                "HOME_URL is not in the settings",
                hint="Set HOME_URL to a valid URL",
                obj=settings,
                id='bootleg.E005',
            )
        )

    return errors


def check_site_name(errors):
    if not settings.site_name():
        errors.append(
            Error(
                "SITE_NAME is not in the settings",
                hint="Set SITE_NAME to the site's name",
                obj=settings,
                id='bootleg.E004',
            )
        )

    return errors


def check_site_domain(errors):
    if not settings.site_domain():
        errors.append(
            Error(
                "SITE_DOMAIN is not in the settings",
                hint="Set SITE_DOMAIN to the site's domain name",
                obj=settings,
                id='bootleg.E004',
            )
        )

    return errors


def check_log_dir(errors):
    dir = settings.log_dir()
    if not file_system.is_writable(dir):
        errors.append(
            Error(
                "LOG_DIR %s is not writable" % dir,
                hint='chmod and or create %s' % dir,
                obj=settings,
                id='bootleg.E003',
            )
        )

    return errors


def check_sql_logging(errors):
    if settings.log_sql() and not settings.DEBUG:
        errors.append(
            Error(
                "LOG_SQL is set to True but DEBUG is False; the SQL won't be logged if DEBUG is False",
                hint='Set DEBUG to True and LOG_SQL to True',
                obj=settings,
                id='bootleg.E002',
            )
        )

    return errors


def check_django_log_level(errors):
    level = settings.get_setting("DJANGO_LOG_LEVEL", "ERROR")
    if level in ["CRITICAL", "FATAL", "NOTSET"]:
        errors.append(
            Error(
                'DJANGO_LOG_LEVEL %s is not allowed' % level,
                hint='Valid levels are: DEBUG, WARNING, ERROR',
                obj=settings,
                id='bootleg.E001',
            )
        )

    return errors


@register()
def check_settings(app_configs, **kwargs):
    errors = check_django_log_level([])
    errors = check_sql_logging(errors)
    errors = check_log_dir(errors)
    errors = check_site_domain(errors)
    errors = check_site_name(errors)
    errors = check_home_url(errors)
    return errors


class BootlegConfig(AppConfig):
    name = 'bootleg'

    def ready(self):
        models.setup_default_site()
