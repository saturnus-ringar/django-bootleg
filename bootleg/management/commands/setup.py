from django.conf import settings
from django.core.management import BaseCommand

from bootleg.conf import bootleg_settings
from bootleg.logging import logging
from bootleg.system.shell import run_command
from bootleg.utils.env import get_virtual_env_dir


class Command(BaseCommand):
    logger = logging.get_logger("bootleg/setup", "bootleg.setup")

    def handle(self, *args, **options):
        self.logger.info("Fixing directories")
        self.fix_dir(settings.LOG_DIR)
        self.fix_dir(settings.LOG_DIR + "cron")
        if settings.DEBUG is False:
            if getattr(settings, "STATIC_ROOT"):
                self.fix_dir(settings.STATIC_ROOT)
            if getattr(settings, "MEDIA_ROOT"):
                self.fix_dir(settings.MEDIA_ROOT)
        self.fix_dir(get_virtual_env_dir())
        self.fix_dir(settings.BASE_DIR)
        self.logger.info("Done with setup")

    def fix_dir(self, directory):
        main_user = bootleg_settings.MAIN_USER
        user_group = bootleg_settings.WEBSERVER_USER_GROUP
        self.logger.info("Fixing directory: [%s]" % directory)
        run_command(["mkdir", "-p", directory])
        run_command(["chmod", "-R", "770", directory])
        run_command(["chown", "-R", main_user + ":" + user_group, directory])
        run_command(["chmod", "-R", "g+s", directory])
