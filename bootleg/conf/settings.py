import collections
import logging

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from bootleg.system import file_system

DEFAULT_FAVICON = "bootleg/img/favicon.png"


class ConfigurationError(Exception):
    pass


def get_setting(attribute, default=None, required=False):
    value = getattr(settings, attribute, default)
    if required and not value:
        raise ConfigurationError("%s must be defined in settings." % attribute)

    return value


def check_log_level(level):
    try:
        logging._checkLevel(level)
    except (ValueError, TypeError):
        raise ConfigurationError("%s: is not a valid log level. Valid levels are: %s"
                                 % (level, logging._levelToName))


def get_debug_settings_value(default, debug_value):
    if settings.DEBUG:
        return debug_value

    return default


class Settings:

    __settings__ = {}

    def __init__(self):
        # init django settings here - to read new value
        try:
            settings._setup()
        except ImproperlyConfigured:
            # django settings may not have been initialized here
            return

        self.setup()

    def get_settings(self):
        return collections.OrderedDict(sorted(self.__settings__.items()))

    def setup(self):
        ####################################################
        # project stuff
        ####################################################
        self.add_setting("ROOT_FOLDER", get_setting("BASE_DIR", required=True))
        last_dir = file_system.get_last_dir(self.ROOT_FOLDER)
        self.add_setting("PROJECT_NAME", last_dir)

        ####################################################
        # db-logging
        ####################################################
        self.add_setting("STORE_DJANGO_LOG_EXCEPTIONS", get_debug_settings_value(True, False))
        self.add_setting("STORE_LOGGED_EXCEPTIONS", True)

        ####################################################
        # logging
        ####################################################
        self.add_setting("LOG_DIR", None)
        self.add_setting("LOG_FORMAT", "%(asctime)s %(levelname)s %(message)s")
        self.add_setting("LOG_DATE_FORMAT",  "%Y-%m-%d %H:%M:%S")
        self.add_setting("LOG_TO_STDOUT", True)
        self.add_setting("LOG_SQL", False)
        self.add_setting("LOG_SQL", False)
        self.add_setting("LOG_LEVEL", "INFO")
        self.add_setting("DJANGO_LOG_LEVEL", get_debug_settings_value("ERROR", "INFO"))

        ####################################################
        # templates
        ####################################################
        self.add_setting("BASE_TEMPLATE", "bootleg/base.html")
        self.add_setting("ADMIN_TEMPLATE", self.BASE_TEMPLATE)
        self.add_setting("NAVIGATION_TEMPLATE", None)
        self.add_setting("SYSTEM_TEMPLATE", "bootleg/system/system.html")
        self.add_setting("DEPLOYMENT_TEMPLATE", "bootleg/system/deployment.html")
        self.add_setting("ERROR_400_TEMPLATE", "bootleg/error/400.html")
        self.add_setting("ERROR_403_TEMPLATE", "bootleg/error/403.html")
        self.add_setting("ERROR_404_TEMPLATE", "bootleg/error/404.html")
        self.add_setting("ERROR_500_TEMPLATE", "bootleg/error/500.html")

        ####################################################
        # site
        ####################################################
        self.add_setting("SITE_NAME", None)
        self.add_setting("SITE_DOMAIN", None)

        ####################################################
        # users/groups
        ####################################################
        self.add_setting("MAIN_USER", last_dir)
        self.add_setting("WEBSERVER_USER", "www-data")
        self.add_setting("MAIN_USER_GROUP", last_dir)
        self.add_setting("WEBSERVER_USER_GROUP", "www-data")

        ####################################################
        # css/html/images
        ####################################################
        self.add_setting("HTML_LANGUAGE_CODE", get_setting("LANGUAGE_CODE", "en")[:2])
        self.add_setting("CSS_FILES", ["bootleg/css/vendor/bootstrap.css"])
        self.add_setting("FAVICON_FILE", DEFAULT_FAVICON)
        self.add_setting("BRANDING_LOGO", None)
        self.add_setting("CONTAINER_CSS_CLASS", "container bg-dark")
        self.add_setting("WRAP_FORMS", True)
        self.add_setting("BOOTSTRAP_3", False)

        ####################################################
        # javascript
        ####################################################
        self.add_setting("JS_DATE_FORMAT", "yyyy-MM-DD")
        self.add_setting("JS_DATETIME_FORMAT", "yyyy-MM-DD hh:ss")

        ####################################################
        # URLs
        ####################################################
        self.add_setting("LOGIN_EXEMPT_URLS_FUNCTION", None)
        self.add_setting("HOME_URL", None, required=True)
        self.add_setting("LOGIN_REDIRECT_URL", get_setting("LOGIN_REDIRECT_URL"), required=True)

        ####################################################
        # misch-ish
        ####################################################
        self.add_setting("PRINT_AT_STARTUP", True)
        self.add_setting("ADD_BUILTINS", True)
        self.add_setting("GOOGLE_ANALYTICS_ACCOUNT", None)
        self.add_setting("PROJECT_ABBR", None)

    def add_setting(self, attribute, default=None, required=False):
        value = get_setting(attribute, default, required=required)
        if attribute not in self.__settings__:
            setattr(self, attribute, value)
            self.__settings__[attribute] = value
