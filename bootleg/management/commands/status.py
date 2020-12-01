from humanize import intcomma

from bootleg.utils import humanize
from colorama import Fore
from django.core.management import BaseCommand

from bootleg.system.system import System
from bootleg.utils.printer import print_heading, print_key_value


class Command(BaseCommand):
    help = "Prints status ...sort of..."

    def handle(self, *args, **options):
        print_heading(Fore.MAGENTA + " Status ".ljust(68))
        system = System()
        print_key_value("Python version", system.get_short_python_version())
        print_key_value("MySQL version", system.mysql_version)
        print_key_value("DB size", humanize.humanize_bytes(system.get_db_size()))
        print_key_value("DB rows", intcomma(system.get_number_of_db_rows()))
        print(Fore.LIGHTBLUE_EX + "Disk usage")
        print(Fore.LIGHTCYAN_EX + system.disk_usage)
        print(Fore.LIGHTBLUE_EX + "Uptime")
        print(Fore.LIGHTCYAN_EX + system.uptime)
        print(Fore.RESET)
