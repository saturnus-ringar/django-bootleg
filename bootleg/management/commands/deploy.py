from bootleg.management.commands.base import BaseCommand

from bootleg import logging
from bootleg.git import git
from django.core import management

from bootleg.utils import utils as bootleg_utils, system
from bootleg.conf import settings as bootleg_settings


class Command(BaseCommand):
    help = 'Deployment...'
    logger = logging.get_logger("deploy")

    def add_arguments(self, parser):
        parser.add_argument(
            '-s', '--soft-deploy', action='store_true', dest='soft_deploy',
            help="Soft deploy without a server restart",
        )

    def handle(self, *args, **options):
        self.logger.info("Deploying %s" % bootleg_settings.project_name())
        self.logger.info("Running git pull")
        self.logger.info(git.git_pull())
        self.logger.info("Installing packages")
        system.pip_install()
        self.logger.info("Migrating")
        management.call_command("migrate")
        self.logger.info("Collecting static")
        management.call_command("collectstatic", interactive=False)
        if not options['soft_deploy']:
            if bootleg_utils.is_apache_context():
                self.logger.info("Restarting Apache")
            elif bootleg_utils.is_gunicorn_context():
                self.logger.info("Restarting Gunicorn")
            else:
                raise ValueError("Could not determine which server type this is running on. Can't restart.")