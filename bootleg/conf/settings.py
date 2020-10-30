import logging
import os

from django.conf import settings, global_settings
from django.urls import reverse

SETTINGS = {}


class ConfigurationError(Exception):
    pass


def get_setting(attribute, default=None, required=False):
    if attribute in SETTINGS:
        return SETTINGS[attribute]

    SETTINGS[attribute] = getattr(settings, attribute, default)

    if required and not SETTINGS[attribute]:
        raise ConfigurationError("%s must be defined in settings." % attribute)

    return SETTINGS[attribute]


def check_log_level(level):
    try:
        logging._checkLevel(level)
    except (ValueError, TypeError):
        raise ConfigurationError("%s: is not a valid log level. Valid levels are: %s"
                                 % (level, logging._levelToName))


def get_error_template(status_code):
    return "bootleg/errors/%s.html" % status_code


####################################################
# project ...stuff...
####################################################

def root_folder():
    return os.path.basename(get_setting("BASE_DIR", required=True))


def project_name():
    return root_folder()


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
    return get_setting("NAVIGATION_TEMPLATE", None, required=True)


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
    return reverse(get_setting("HOME_URL", None, required=True))


def login_redirect_url():
    url = get_setting("LOGIN_REDIRECT_URL")
    if url == global_settings.LOGIN_REDIRECT_URL:
        # override django's default url
        url = str(reverse("dev_null"))
    return url


def get_login_exempt_urls_function():
    return get_setting("LOGIN_EXEMPT_URLS_FUNCTION", None)
