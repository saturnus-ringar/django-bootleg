__version__ = "0.12o"
default_app_config = "bootleg.apps.BootlegConfig"


def setup():
    from bootleg import bootstrap
    from bootleg.conf import bootleg_settings
    from bootleg.logging import logging
    from bootleg.settings import set_django_settings
    # setup settings (again - they are run on initial imports) to read django settings
    bootleg_settings.setup()
    # set django settings
    set_django_settings()

    if bootleg_settings.ADD_BUILTINS:
        logging.add_builtins()

    if bootleg_settings.PRINT_AT_STARTUP:
        bootstrap.startup_print()
