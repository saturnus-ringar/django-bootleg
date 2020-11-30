from bootleg.system.shell import run_command

from bootleg.logging import logging
from django.core import management

from bootleg.conf import bootleg_settings
from bootleg.management.commands.base import UserRequirementCommand
from bootleg.system import utils, git
from bootleg.utils import env


class Command(UserRequirementCommand):
    help = 'Deployment...'
    logger = logging.get_logger("deploy", "bootleg.deploy")

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
            if env.is_apache_from_cli():
                self.logger.info("Restarting Apache")
                run_command(["systemctl", "restart", "apache2"])
            elif env.is_gunicorn_from_cli():
                self.logger.info("Restarting Gunicorn")
                run_command(["systemctl", "restart", "gunicorn.socket"])
            else:
                raise ValueError("Could not determine which server type this is running on. Can't restart.")
