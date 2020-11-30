__version__ = "0.98o"
default_app_config = "bootleg.apps.BootlegConfig"


def setup():
    from bootleg import bootstrap
    from bootleg.conf import bootleg_settings
    from bootleg.logging import logging
    # setup settings (again - they are run on initial imports) to read django settings
    bootleg_settings.setup()

    if bootleg_settings.ADD_BUILTINS:
        logging.add_builtins()

    if bootleg_settings.PRINT_AT_STARTUP:
        bootstrap.startup_print()
