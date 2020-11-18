import bootleg
from colorama import Fore, Back, Style
from django.conf import settings
from django.db import connection

from bootleg.conf import bootleg_settings
from bootleg.utils import models


def print_setting(text, value):
    color = Fore.LIGHTCYAN_EX
    if isinstance(value, bool):
        if value:
            color = Fore.LIGHTGREEN_EX
        else:
            color = Fore.RED

    print(Fore.LIGHTBLUE_EX + text.ljust(40) + "\t" + color + str(value))


def startup_print():
    print(Fore.LIGHTBLUE_EX + "  .-.     .-.     .-.     .-.     .-.     .-.     .-.     .-.     .-.     .-.")
    print(" " + Fore.BLUE + "∞ " + Fore.LIGHTMAGENTA_EX + "Running django bootleg version: " +Fore.LIGHTGREEN_EX + bootleg.__version__
          + Fore.BLUE + " ∞")
    print(Fore.LIGHTBLUE_EX + "'     `-'     `-'     `-'     `-'     `-'     `-'     `-'     `-'     `-'     `")
    if getattr(settings, "DEBUG"):
        print(Fore.LIGHTBLUE_EX + "We're running in " + Fore.LIGHTGREEN_EX + "DEBUG")
    else:
        print(Fore.LIGHTBLUE_EX + "We're NOT running in " + Fore.RED + "DEBUG")

    print_setting("Database Backend", connection.vendor)
    print_setting("Database", connection.settings_dict['NAME'])
    print_setting("Log Dir", bootleg_settings.LOG_DIR)
    print_setting("Log Level", bootleg_settings.LOG_LEVEL)
    print_setting("Django Log Level",  bootleg_settings.DJANGO_LOG_LEVEL)
    print_setting("Static Root", getattr(settings, "STATIC_ROOT"))
    print_setting("Static URL", getattr(settings, "STATIC_URL"))
    print_setting("Media Root", getattr(settings, "MEDIA_ROOT"))
    print_setting("Media URL", getattr(settings, "MEDIA_URL"))

    editable_models = models.get_editable_models()
    if editable_models:
        print_setting("Editable models", str(models.get_editable_models()))

    if bootleg_settings.LOG_SQL:
        print(Fore.LIGHTGREEN_EX + "* Logging SQL")

    if bootleg_settings.STORE_LOGGED_EXCEPTIONS:
        print(Fore.LIGHTGREEN_EX + "* Storing internal log exceptions")

    if bootleg_settings.STORE_DJANGO_LOG_EXCEPTIONS:
        print(Fore.LIGHTGREEN_EX + "* Storing Django log exceptions")

    custom_settings_to_print = getattr(settings, "SETTINGS_TO_PRINT", None)
    if custom_settings_to_print:
        print(Fore.LIGHTBLUE_EX + "Custom settings")
        for setting, value in custom_settings_to_print.items():
            print_setting(setting, value)

    print(Style.RESET_ALL)
