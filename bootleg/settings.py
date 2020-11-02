from django.conf import settings

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

COMPRESS_CSS_FILTERS = ['compressor.filters.css_default.CssAbsoluteFilter', 'compressor.filters.cssmin.CSSMinFilter']

log_dir = getattr(settings, "LOG_DIR")
django_log_level = getattr(settings, "DJANGO_LOG_LEVEL", "INFO")

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
            'level': django_log_level,
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
            'level': django_log_level
        },
    },
}

LOGGING["loggers"]["django.db.backends"] = {
    'level': 'DEBUG',  # always debug on this one
    'handlers': ['sql']
}
