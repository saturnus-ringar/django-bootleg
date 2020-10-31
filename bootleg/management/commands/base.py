from bootleg.nix import nix
from django.core.management import BaseCommand
from bootleg.settings import settings as bootleg_settings


class UserError(Exception):
    pass


class BaseCommand(BaseCommand):

    def __init__(self, stdout=None, stderr=None, no_color=False, force_color=False):
        if not nix.is_current_user(bootleg_settings.main_user()):
            raise UserError("This command must be run by the user: %s" % bootleg_settings.main_user())
        super().__init__(stdout, stderr, no_color, force_color)

    def handle(self, *args, **options):
        pass
