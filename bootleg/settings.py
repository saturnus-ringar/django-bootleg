from bootleg.conf import settings
from bootleg.logging import logging
from bootleg.utils import file_system
from django.conf import settings as django_settings
# somewhat ugly to change the django settings at runtime ...nevertheless...

#####################################################
# django settings
#####################################################

SITE_ID = 1

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

COMPRESS_CSS_FILTERS = ['compressor.filters.css_default.CssAbsoluteFilter',  'compressor.filters.cssmin.CSSMinFilter']

#####################################################
# logging
#####################################################

log_dir = settings.log_dir()
log_level = settings.log_level()

if file_system.is_writable(log_dir):
    django_settings.LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'verbose': {
                'format': settings.log_format(),
                'datefmt': settings.log_date_format(),
            }
        },
        'handlers': {
            'django': {
                'level': log_level,
                'class': 'bootleg.logging.handlers.DjangoLogHandler',
                'filename': log_dir + 'django.log',
                'formatter': 'verbose'
            },
            'sql': {
                'level': 'DEBUG', # static DEBUG level on this one
                'class': 'bootleg.logging.handlers.FileHandler',
                'filename': log_dir + 'sql.log',
                'formatter': 'verbose'
            },
        },
        'loggers': {
            'django': {
                'handlers': ['django'],
                'level': log_level
            },
        },
    }

    if settings.log_sql():
        django_settings.LOGGING["loggers"]["django.db.backends"] = {
            'level': 'DEBUG', # always debug on this one
            'handlers': ['sql']
        }

# read settings to validate at startup
settings.navigation_template()

if settings.add_builtins():
    logging.add_builtins()
