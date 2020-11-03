from django.core import management

from bootleg import logging
from bootleg.conf import bootleg_settings
from bootleg.management.commands.base import BaseCommand
from bootleg.system import utils, git
from bootleg.utils import env


class Command(BaseCommand):
    help = 'Deployment...'
    logger = logging.get_logger("bootleg.deploy")

    def add_arguments(self, parser):
        parser.add_argument(
            '-s', '--soft-deploy', action='store_true', dest='soft_deploy',
            help="Soft deploy without a server restart",
        )

    def handle(self, *args, **options):
        self.logger.info("Deploying %s" % bootleg_settings.PROJECT_NAME)
        self.logger.info("Running git pull")
        self.logger.info(git.git_pull())
        self.logger.info("Installing packages")
        utils.pip_install()
        self.logger.info("Migrating")
        management.call_command("migrate")
        self.logger.info("Collecting static")
        management.call_command("collectstatic", interactive=False)
        if not options['soft_deploy']:
            if env.is_apache():
                self.logger.info("Restarting Apache")
            elif env.is_gunicorn():
                self.logger.info("Restarting Gunicorn")
            else:
                raise ValueError("Could not determine which server type this is running on. Can't restart.")
