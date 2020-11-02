import bootleg
from colorama import Fore, Style
from django.conf import settings
from django.db import connection

from bootleg.conf import bootleg_settings
from bootleg.utils import models


def print_setting(text, value):
    print(Fore.LIGHTYELLOW_EX + text.ljust(40) + "\t" + str(value))


def startup_print():
    print(Fore.LIGHTBLUE_EX + "*********************************************************************")
    print("Running django bootleg version: %s" % bootleg.__version__)
    if getattr(settings, "DEBUG"):
        print(Fore.LIGHTYELLOW_EX + "We're running in " + Fore.MAGENTA + "debug")
    else:
        print(Fore.LIGHTYELLOW_EX + "We're NOT running in " + Fore.LIGHTBLUE_EX + "debug")

    print_setting("Database backend", connection.vendor)
    print_setting("Database", connection.settings_dict['NAME'])
    print_setting("Log-dir", bootleg_settings.LOG_DIR)
    print_setting("Log level", bootleg_settings.LOG_LEVEL)
    print_setting("Django log level",  bootleg_settings.DJANGO_LOG_LEVEL)
    print_setting("Static root", getattr(settings, "STATIC_ROOT"))
    print_setting("Static url", getattr(settings, "STATIC_URL"))
    print_setting("Media root", getattr(settings, "MEDIA_ROOT"))
    print_setting("Media url", getattr(settings, "MEDIA_URL"))

    editable_models = models.get_editable_models()
    if editable_models:
        print_setting("Editable models", str(models.get_editable_models()))

    if bootleg_settings.LOG_SQL:
        print(Fore.GREEN + "* Logging SQL")

    if bootleg_settings.STORE_LOGGED_EXCEPTIONS:
        print(Fore.GREEN + "* Storing internal log exceptions")

    if bootleg_settings.STORE_DJANGO_LOG_EXCEPTIONS:
        print(Fore.GREEN + "* Storing Django log exceptions")

    custom_settings_to_print = getattr(settings, "SETTINGS_TO_PRINT")
    if custom_settings_to_print:
        print(Fore.LIGHTBLUE_EX + "Custom settings")
        for setting, value in custom_settings_to_print.items():
            print_setting(setting, value)

    print(Fore.LIGHTBLUE_EX + "*********************************************************************")
    print(Style.RESET_ALL)
