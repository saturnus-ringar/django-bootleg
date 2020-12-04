from bootleg.system.shell import run_command

from bootleg.logging import logging
from django.core import management

from bootleg.conf import bootleg_settings
from bootleg.management.commands.base import UserRequirementCommand
from bootleg.system import utils, git
from bootleg.utils import env


class Command(UserRequirementCommand):
    logger = logging.get_logger("deploy", "bootleg.deploy")

    def add_arguments(self, parser):
        parser.add_argument("-s", "--soft", action="store_true", default=False,
                            help="Soft deploy without a server restart")

    def handle(self, *args, **options):
        if not env.is_venv():
            raise RuntimeError("This must be run in an virtual env")

        self.logger.info("Deploying %s" % bootleg_settings.PROJECT_NAME)

        if options["soft"]:
            self.logger.info("Running soft deploy. Won't restart the server.")

        self.logger.info(git.git_pull())
        utils.pip_install()
        management.call_command("migrate")
        management.call_command("collectstatic", interactive=False)
        if not options["soft"]:
            if env.is_apache_from_cli():
                self.logger.info("Restarting apache")
                run_command(["sudo", "systemctl", "restart", "apache2"])
            elif env.is_gunicorn_from_cli():
                self.logger.info("Restarting guincorn")
                run_command(["sudo", "systemctl", "restart", "gunicorn.socket"])
            else:
                raise ValueError("Could not determine which server type this is running on. Can't restart.")

        self.logger.info("Done with deploy")
