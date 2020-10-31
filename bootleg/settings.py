from bootleg.system import file_system
from bootleg.conf.settings import bootleg_settings
from django.conf import settings

# somewhat ugly to change the django settings at runtime ...nevertheless...

#####################################################
# django settings
#####################################################

if not settings.is_overridden("SITE_ID"):
    settings.SITE_ID = 1

#####################################################
# django tables 2
#####################################################

settings.DJANGO_TABLES2_TEMPLATE = "django_tables2/bootstrap-responsive.html"

#####################################################
# crispy forms
#####################################################

settings.CRISPY_TEMPLATE_PACK = "bootstrap4"

#####################################################
# django compress
#####################################################

if not settings.is_overridden("COMPRESS_CSS_FILTERS"):
    settings.COMPRESS_CSS_FILTERS = ['compressor.filters.css_default.CssAbsoluteFilter',  'compressor.filters.cssmin.CSSMinFilter']

#####################################################
# logging
#####################################################


if file_system.is_writable(bootleg_settings.LOG_DIR):
    settings.LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'verbose': {
                'format': bootleg_settings.LOG_FORMAT,
                'datefmt': bootleg_settings.LOG_DATE_FORMAT,
            }
        },
        'handlers': {
            'django': {
                'level': bootleg_settings.DJANGO_LOG_LEVEL,
                'class': 'bootleg.logging.handlers.DjangoLogHandler',
                'filename':  bootleg_settings.LOG_DIR + 'django.log',
                'formatter': 'verbose'
            },
            'sql': {
                'level': 'DEBUG', # static DEBUG level on this one
                'class': 'bootleg.logging.handlers.FileHandler',
                'filename':  bootleg_settings.LOG_DIR + 'sql.log',
                'formatter': 'verbose'
            },
        },
        'loggers': {
            'django': {
                'handlers': ['django'],
                'level': bootleg_settings.DJANGO_LOG_LEVEL
            },
        },
    }

    if bootleg_settings.LOG_SQL:
        settings.LOGGING["loggers"]["django.db.backends"] = {
            'level': 'DEBUG', # always debug on this one
            'handlers': ['sql']
        }
