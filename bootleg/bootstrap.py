from colorama import Fore, Style
from django.conf import settings
from django.db import connection
from bootleg.conf import settings as bootleg_settings
from bootleg.utils import models


def startup_print():
    print(Fore.LIGHTBLUE_EX + "*********************************************************************")
    if getattr(settings, "DEBUG"):
        print(Fore.LIGHTYELLOW_EX + "We're running in " + Fore.MAGENTA + "debug")
    else:
        print(Fore.LIGHTYELLOW_EX + "We're NOT running in " + Fore.LIGHTBLUE_EX + "debug")

    print(Fore.LIGHTYELLOW_EX + "Database backend:\t" + connection.vendor)
    print("Using database:\t\t" + connection.settings_dict['NAME'])
    print("Log-dir:\t\t" + bootleg_settings.log_dir())
    print("Log level:\t\t" + bootleg_settings.log_level())
    print("Django log level:\t" + bootleg_settings.django_log_level())
    print("Static root:\t\t" + getattr(settings, "STATIC_ROOT"))
    print("Static url:\t\t" + getattr(settings, "STATIC_URL"))
    print("Media root:\t\t" + getattr(settings, "MEDIA_ROOT"))
    print("Media url:\t\t" + getattr(settings, "MEDIA_URL"))

    editable_models = models.get_editable_models()
    if editable_models:
        print("Editable models:\t" + str(models.get_editable_models()))

    if bootleg_settings.log_sql():
        print(Fore.GREEN + "* Logging SQL")

    if bootleg_settings.store_logged_exception():
        print(Fore.GREEN + "* Storing internal log exceptions")

    if bootleg_settings.store_django_log_exceptions():
        print(Fore.GREEN + "* Storing Django log exceptions")

    print(Fore.LIGHTBLUE_EX + "*********************************************************************")
    print(Style.RESET_ALL)
