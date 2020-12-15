from colorama import Fore, Style
from django.conf import settings
from django.db import connection

import bootleg
from bootleg.conf import bootleg_settings
from bootleg.utils import models
from bootleg.utils.env import use_elastic_search
from bootleg.utils.printer import print_key_value, print_heading


def startup_print():
    print_heading(Fore.LIGHTMAGENTA_EX + "Running django bootleg version: " + Fore.LIGHTGREEN_EX + bootleg.__version__)

    if getattr(settings, "DEBUG"):
        print(Fore.LIGHTBLUE_EX + "We're running in " + Fore.LIGHTGREEN_EX + "DEBUG")
    else:
        print(Fore.LIGHTBLUE_EX + "We're NOT running in " + Fore.RED + "DEBUG")

    print_key_value("Database Backend", connection.vendor)
    print_key_value("Database", connection.settings_dict['NAME'])
    print_key_value("Log Dir", bootleg_settings.LOG_DIR)
    print_key_value("Log Level", bootleg_settings.LOG_LEVEL)
    print_key_value("Django Log Level",  bootleg_settings.DJANGO_LOG_LEVEL)
    print_key_value("Static Root", getattr(settings, "STATIC_ROOT"))
    print_key_value("Static URL", getattr(settings, "STATIC_URL"))
    print_key_value("Media Root", getattr(settings, "MEDIA_ROOT"))
    print_key_value("Media URL", getattr(settings, "MEDIA_URL"))

    editable_models = models.get_editable_models_verbose_names()
    if editable_models:
        print_key_value("Editable models", str(editable_models))

    search_models = models.get_search_models_verbose_names()
    if search_models:
        if use_elastic_search():
            print_key_value("Search models", str(search_models))
        else:
            print(Fore.LIGHTYELLOW_EX + "Elastic search is disabled.")

    if bootleg_settings.LOG_SQL:
        print(Fore.LIGHTGREEN_EX + "Logging SQL")

    if bootleg_settings.STORE_LOGGED_EXCEPTIONS:
        print(Fore.LIGHTGREEN_EX + "Storing internal log exceptions")

    if bootleg_settings.STORE_DJANGO_LOG_EXCEPTIONS:
        print(Fore.LIGHTGREEN_EX + "Storing Django log exceptions")

    custom_settings_to_print = getattr(settings, "SETTINGS_TO_PRINT", None)
    if custom_settings_to_print:
        for setting, value in custom_settings_to_print.items():
            print_key_value(setting, value)

    print(Style.RESET_ALL)
