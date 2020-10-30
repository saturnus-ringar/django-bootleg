from bootleg import bootstrap
from django.utils.version import get_version

VERSION = (0, 0, 12, 'beta', 0)
__version__ = get_version(VERSION)

default_app_config = "bootleg.apps.BootlegConfig"


def setup():
    from bootleg.conf import settings as bootleg_settings
    from bootleg.logging import logging

    if bootleg_settings.add_builtins():
        logging.add_builtins()

    if bootleg_settings.print_at_startup():
        bootstrap.startup_print()
