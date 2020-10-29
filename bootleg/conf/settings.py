import logging
import os

from django.conf import settings, global_settings
from django.core.checks import Error, register
# setup settings ... again :|
# it takes something like "0.09429597854614258 seconds"
from django.urls import reverse

from bootleg.utils import file_system

SETTINGS = {}
settings._setup()


def check_home_url(errors):
    if not home_url():
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
    if not site_name():
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
    if not site_domain():
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
    dir = log_dir()
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
    if log_sql() and not settings.DEBUG:
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
    level = get_setting("DJANGO_LOG_LEVEL", "ERROR")
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


class ConfigurationError(Exception):
    pass


def get_setting(attribute, default=None, optional=True):
    if attribute in SETTINGS:
        return SETTINGS[attribute]

    SETTINGS[attribute] = getattr(settings, attribute, default)

    if not optional and not SETTINGS[attribute]:
        raise ConfigurationError("%s must be defined in settings." % attribute)

    return SETTINGS[attribute]


def check_log_level(attribute, default):
    level = get_setting(attribute, default)
    try:
        logging._checkLevel(level)
    except ValueError:
        raise ConfigurationError("%s: (%s) is not a valid log level. Valid levels are: %s"
                                 % (attribute, level, logging._levelToName))


def get_error_template(status_code):
    return "bootleg/errors/%s.html" % status_code


####################################################
# db-logging
####################################################

def store_django_log_exceptions():
    default = False
    if not settings.DEBUG:
        default = True
    return get_setting("STORE_DJANGO_LOG_EXCEPTIONS", default)


def store_logged_exception():
    return get_setting("STORE_LOGGED_EXCEPTIONS", True)

####################################################
# logging
####################################################


def add_builtins():
    return get_setting("ADD_BUILTINS", True)


def log_dir():
    dir = get_setting("LOG_DIR", fail_log_path())
    return os.path.join(dir, '')


def log_format():
    return get_setting("LOG_FORMAT", "%(asctime)s %(levelname)s %(message)s")


def log_date_format():
    return get_setting("LOG_DATE_FORMAT", "%Y-%m-%d %H:%M:%S")


def log_to_stdout():
    return get_setting("LOG_TO_STDOUT", True)


def log_sql():
    return get_setting("LOG_SQL", False)


def django_log_level():
    return get_setting("DJANGO_LOG_LEVEL", "ERROR")


def log_level():
    return get_setting("LOG_LEVEL", "INFO")


####################################################
# templates
####################################################

def base_template():
    return get_setting("BASE_TEMPLATE", "bootleg/base.html")


def navigation_template():
    return get_setting("NAVIGATION_TEMPLATE", None, optional=False)


def template_400():
    return get_setting("ERROR_400_TEMPLATE", get_error_template(400))


def template_403():
    return get_setting("ERROR_403_TEMPLATE", get_error_template(403))


def template_404():
    return get_setting("ERROR_404_TEMPLATE", get_error_template(404))


def template_500():
    return get_setting("ERROR_500_TEMPLATE", get_error_template(500))


####################################################
# site
####################################################

def site_name():
    return get_setting("SITE_NAME", None)


def site_domain():
    return get_setting("SITE_DOMAIN", None)


def site_id():
    return get_setting("SITE_ID")


####################################################
# misc-ish
####################################################


def print_at_startup():
    return get_setting("PRINT_AT_STARTUP", True)


def fail_log_path():
    return "/dev/null"


def html_language_code():
    return get_setting("LANGUAGE_CODE", "en")[:2]


def css_file():
    return get_setting("CSS_FILE", "bootleg/css/vendor/bootstrap.css")


def container_css_class():
    return get_setting("CONTAINER_CSS_CLASS", "container bg-dark")


def favicon_file():
    return get_setting("FAVICON_FILE", "bootleg/img/favicon.png")


def google_analytics_account():
    return get_setting("GOOGLE_ANALYTICS_ACCOUNT", None)


def home_url():
    return reverse(get_setting("HOME_URL", None, optional=False))


def login_redirect_url():
    url = get_setting("LOGIN_REDIRECT_URL")
    if url == global_settings.LOGIN_REDIRECT_URL:
        # override django's default url
        url = str(reverse("dev_null"))
    return url


def get_login_exempt_urls_function():
    return get_setting("LOGIN_EXEMPT_URLS_FUNCTION", None)
