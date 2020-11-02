import logging

from django.conf import settings

SETTINGS_OBJ = None


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


def get_debug_settings_value(default, if_debug_value):
    if not settings.DEBUG:
        return if_debug_value
    else:
        return default


class Settings:

    __settings__ = {}

    def __init__(self):
        # setup django settings to get the local settings value
        settings._setup()
        self.setup()
        self.set_django_settings()
        # do another setup of the django settings to add these new values
        settings._setup()

    def setup(self):
        ####################################################
        # project stuff
        ####################################################
        self.add_setting("ROOT_FOLDER", get_setting("BASE_DIR", required=True))
        self.add_setting("PROJECT_NAME", get_setting("BASE_DIR", required=True))

        ####################################################
        # db-logging
        ####################################################
        self.add_setting("STORE_DJANGO_LOG_EXCEPTIONS", True, False)
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
        self.add_setting("ERROR_400_TEMPLATE", None)
        self.add_setting("ERROR_403_TEMPLATE", None)
        self.add_setting("ERROR_404_TEMPLATE", None)
        self.add_setting("ERROR_500_TEMPLATE", None)

        ####################################################
        # site
        ####################################################
        self.add_setting("SITE_NAME", None)
        self.add_setting("SITE_DOMAIN", None)
        self.add_setting("SITE_ID")

        ####################################################
        # users/groups
        ####################################################
        self.add_setting("MAIN_USER", self.ROOT_FOLDER)
        self.add_setting("WEBSERVER_USER", "www-data")
        self.add_setting("MAIN_USER_GROUP", self.ROOT_FOLDER)
        self.add_setting("WEBSERVER_USER_GROUP", "www-data")

        ####################################################
        # git
        ####################################################
        self.add_setting("GIT_URL", None)

        ####################################################
        # css/html/images
        ####################################################
        self.add_setting("HTML_LANGUAGE_CODE", get_setting("LANGUAGE_CODE", "en")[:2])
        self.add_setting("CSS_FILE", "bootleg/css/vendor/bootstrap.css")
        self.add_setting("CONTAINER_CSS_CLASS", "container bg-dark")
        self.add_setting("FAVICON_FILE", "bootleg/img/favicon.png")
        self.add_setting("CONTAINER_CSS_CLASS", "container bg-dark")

        ####################################################
        # URLs
        ####################################################
        self.add_setting("LOGIN_EXEMPT_URLS_FUNCTION", None)
        self.add_setting("HOME_URL", None, required=True)

        url = get_setting("LOGIN_REDIRECT_URL")
        #if url == global_settings.LOGIN_REDIRECT_URL:
        #    #override django's default url
        #    url = str(reverse_lazy("bootleg:dev_null"))
        self.add_setting("LOGIN_REDIRECT_URL", url, required=True)

        ####################################################
        # misch-ish
        ####################################################
        self.add_setting("PRINT_AT_STARTUP", True)
        self.add_setting("ADD_BUILTINS", True)
        self.add_setting("GOOGLE_ANALYTICS_ACCOUNT", None)

    def add_setting(self, attribute, default=None, required=False):
        value = get_setting(attribute, default, required=required)
        if attribute not in self.__settings__:
            setattr(self, attribute, value)

    def set_django_settings(self):
        # somewhat ugly to set this at runtime ...nevertheless..

        #####################################################
        # django settings
        #####################################################

        if not getattr(settings, "SITE_ID", None):
            settings.SITE_ID = 1

        #####################################################
        # django tables 2
        #####################################################

        settings.DJANGO_TABLES2_TEMPLATE = "django_tables2/bootstrap-responsive.html"

        #####################################################
        # crispy forms
        #####################################################

        settings.CRISPY_TEMPLATE_PACK = "bootstrapkuekn"

        #####################################################
        # django compress
        #####################################################

        if getattr(settings, "COMPRESS_CSS_FILTERS", None):
            settings.COMPRESS_CSS_FILTERS = ['compressor.filters.css_default.CssAbsoluteFilter',
                                             'compressor.filters.cssmin.CSSMinFilter']

        #####################################################
        # logging
        #####################################################

            settings.LOGGING = {
                'version': 1,
                'disable_existing_loggers': False,
                'formatters': {
                    'verbose': {
                        'format': self.LOG_FORMAT,
                        'datefmt': self.LOG_DATE_FORMAT,
                    }
                },
                'handlers': {
                    'django': {
                        'level': self.DJANGO_LOG_LEVEL,
                        'class': 'bootleg.logging.handlers.DjangoLogHandler',
                        'filename':  self.LOG_DIR + 'django.log',
                        'formatter': 'verbose'
                    },
                    'sql': {
                        'level': 'DEBUG', # static DEBUG level on this one
                        'class': 'bootleg.logging.handlers.FileHandler',
                        'filename':  self.LOG_DIR + 'sql.log',
                        'formatter': 'verbose'
                    },
                },
                'loggers': {
                    'django': {
                        'handlers': ['django'],
                        'level': self.DJANGO_LOG_LEVEL
                    },
                },
            }

            if self.LOG_SQL:
                settings.LOGGING["loggers"]["django.db.backends"] = {
                    'level': 'DEBUG', # always debug on this one
                    'handlers': ['sql']
                }
