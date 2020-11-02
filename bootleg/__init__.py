#from bootleg import bootstrap
#from django.utils.version import get_version

VERSION = (0, 0, 13, 'beta', 0)
#__version__ = get_version(VERSION)
__version__ = "0.11o"

default_app_config = "bootleg.apps.BootlegConfig"


def setup():
    from bootleg.conf import bootleg_settings
    from bootleg.logging import logging
    from bootleg.settings import set_django_settings
    # setup settings (again - they are run on initial imports) to read django settings
    bootleg_settings.setup()
    # set django settings
    set_django_settings()

    if bootleg_settings.ADD_BUILTINS:
        logging.add_builtins()

    #if bootleg_settings.PRINT_AT_STARTUP:
    #    bootstrap.startup_print()
