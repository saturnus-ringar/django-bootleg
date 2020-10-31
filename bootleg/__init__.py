from bootleg import bootstrap
from django.utils.version import get_version

VERSION = (0, 0, 13, 'beta', 0)
__version__ = get_version(VERSION)

default_app_config = "bootleg.apps.BootlegConfig"


def setup():
    print("SETUP!")
    from bootleg.conf.settings import bootleg_settings
    from bootleg.logging import logging

    if bootleg_settings.ADD_BUILTINS:
        logging.add_builtins()

    if bootleg_settings.PRINT_AT_STARTUP:
        bootstrap.startup_print()
