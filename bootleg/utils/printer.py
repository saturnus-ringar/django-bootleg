from django.contrib.humanize.templatetags.humanize import intcomma

import bootleg
from colorama import Fore


def print_heading(text):
    print(Fore.LIGHTBLUE_EX + "  .-.     .-.     .-.     .-.     .-.     .-.     .-.     .-.     .-.     .-.")
    print(Fore.BLUE + " ∞ " + text + Fore.BLUE + " ∞")
    print(Fore.LIGHTBLUE_EX + "'     `-'     `-'     `-'     `-'     `-'     `-'     `-'     `-'     `-'     `")


def print_small_heading(text):
    print(Fore.LIGHTBLUE_EX + "∞ " + Fore.LIGHTMAGENTA_EX + text + Fore.LIGHTBLUE_EX + " ∞ ")


def print_bootleg():
    print_heading(" " + Fore.BLUE + "∞ " + Fore.LIGHTMAGENTA_EX + "Running django bootleg version: " + Fore.LIGHTGREEN_EX
          + bootleg.__version__
          + Fore.BLUE + " ∞")


def print_key_value(key, value):
    color = Fore.LIGHTCYAN_EX
    if isinstance(value, bool):
        if value:
            color = Fore.LIGHTGREEN_EX
        else:
            color = Fore.RED

    if isinstance(value, int):
        value = intcomma(value)

    print(Fore.LIGHTBLUE_EX + key.ljust(40) + "\t" + color + str(value))
