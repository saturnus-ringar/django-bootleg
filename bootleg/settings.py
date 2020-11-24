import os

from bootleg.conf.settings import get_setting, get_debug_settings_value, check_log_level, ConfigurationError
from django.conf import settings

LOG_FORMAT = '%(asctime)s %(levelname)s %(message)s'
LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'


class NotWritableError(Exception):
    pass


BOOTLEG_SETTINGS_IMPORTED = True

#####################################################
# django settings
#####################################################

SITE_ID = 1

print(settings.DATETIME_FORMAT)

if not settings.is_overridden("DATETIME_FORMAT"):
    DATETIME_FORMAT = "Y-m-d H:i:s"

if not settings.is_overridden("DATETIME_FORMAT"):
    DATE_FORMAT = "Y-m-d"

if not settings.is_overridden("STATIC_ROOT"):
    STATIC_ROOT = "/static/"

if not settings.is_overridden("MEDIA_ROOT"):
    MEDIA_ROOT = "/media/"

#####################################################
# django tables 2
#####################################################

DJANGO_TABLES2_TEMPLATE = "django_tables2/bootstrap-responsive.html"

#####################################################
# crispy forms
#####################################################

CRISPY_TEMPLATE_PACK = "bootstrap4"

#####################################################
# django compress
#####################################################

COMPRESS_CSS_FILTERS = ['compressor.filters.css_default.CssAbsoluteFilter', 'compressor.filters.cssmin.CSSMinFilter']

log_dir = get_setting("LOG_DIR")

if not log_dir:
    raise ConfigurationError("LOG_DIR must be defined in the settings.")

if not os.access(log_dir, os.W_OK):
    raise NotWritableError("LOG_DIR: %s is not writable" % log_dir)

DJANGO_LOG_LEVEL = get_setting("DJANGO_LOG_LEVEL", get_debug_settings_value("ERROR", "INFO"))
check_log_level(DJANGO_LOG_LEVEL)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(asctime)s %(levelname)s %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        }
    },
    'handlers': {
        'django': {
            'level': DJANGO_LOG_LEVEL,
            'class': 'bootleg.logging.handlers.DjangoLogHandler',
            'filename': log_dir + 'django.log',
            'formatter': 'verbose'
        },
        'sql': {
            'level': 'DEBUG',  # static DEBUG level on this one
            'class': 'bootleg.logging.handlers.FileHandler',
            'filename': log_dir + 'sql.log',
            'formatter': 'verbose'
        },
    },
    'loggers': {
        'django': {
            'handlers': ['django'],
            'level': DJANGO_LOG_LEVEL
        },
    },
}

log_sql = getattr(settings, "LOG_SQL", None)
if log_sql and log_sql is True:
    LOGGING["loggers"]["django.db.backends"] = {
        'level': 'DEBUG',  # always debug on this one
        'handlers': ['sql']
    }
