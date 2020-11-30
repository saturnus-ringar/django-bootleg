
from django.core.management import BaseCommand
from bootleg.conf import bootleg_settings
from bootleg.system import nix


class UserError(Exception):
    pass


class UserRequirementCommand(BaseCommand):

    def __init__(self, stdout=None, stderr=None, no_color=False, force_color=False):
        if not nix.is_current_user(bootleg_settings.MAIN_USER):
            raise UserError("This command must be run by the user: %s" % bootleg_settings.MAIN_USER)
        super().__init__(stdout, stderr, no_color, force_color)

    def handle(self, *args, **options):
        pass
