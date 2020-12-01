from bootleg.system import nix

from bootleg.system.shell import run_command

from bootleg.logging import logging
from django.conf import settings
from bootleg.conf import bootleg_settings
from bootleg.management.commands.base import UserRequirementCommand
from bootleg.utils.env import get_virtual_env_path


class Command(UserRequirementCommand):
    logger = logging.get_logger("setup", "bootleg.setup")

    def handle(self, *args, **options):
        self.logger.info("Fixing directories")
        self.fix_dir(settings.LOG_DIR)
        self.fix_dir(settings.LOG_DIR + "cron")
        if getattr(settings, "STATIC_ROOT"):
            self.fix_dir(settings.STATIC_ROOT)
        if getattr(settings, "MEDIA_ROOT"):
            self.fix_dir(settings.MEDIA_ROOT)
        self.fix_dir(get_virtual_env_path())
        self.fix_dir(settings.BASE_DIR)
        self.logger.info("Done with setup")

    def fix_dir(self, directory):
        main_user = bootleg_settings.MAIN_USER
        user_group = bootleg_settings.WEBSERVER_USER_GROUP
        self.logger.info("Fixing directory: [%s]" % directory)
        run_command(["mkdir", "-p", directory])
        run_command(["chmod", "-R", "770", directory])
        run_command(["chown", "-R", main_user + ":" + user_group, directory])
        run_command(["chown", "-R", "g+s", directory])


'''
#!/bin/bash
mkdir -p /var/log/gigguide/
chmod -R 770 /var/log/gigguide/
chown -R gigguide:www-data /var/log/gigguide/
chmod -R g+s /var/log/gigguide/

mkdir -p /var/log/gigguide/cron/
chmod -R 770 /var/log/gigguide/cron/
chown -R gigguide:www-data /var/log/gigguide/cron/
chmod -R g+s /var/log/gigguide/cron/

mkdir -p /var/www/gigguide/static/
chmod -R 770 /var/www/gigguide/static/
chown -R gigguide:www-data /var/www/gigguide/static/
chmod -R g+s /var/www/gigguide/static/

mkdir -p /var/www/gigguide/media/
chmod -R 770 /var/www/gigguide/media/
chown -R gigguide:www-data /var/www/gigguide/media/
chmod -R g+s /var/www/gigguide/media/

chmod -R 770 /home/gigguide/env/
chown -R gigguide:www-data /home/gigguide/env/
chmod -R g+s /home/gigguide/env/

chmod -R 770 /home/gigguide/gigguide/
chown -R gigguide:www-data /home/gigguide/gigguide/
chmod -R g+s /home/gigguide/gigguide/

mkdir -p /home/gigguide/backup/
chmod -R 770 /home/gigguide/backup/
chown -R gigguide:gigguide /home/gigguide/backup/
chmod -R g+s /home/gigguide/backup/

touch /home/gigguide/backup/gigguide.sql
chmod 770 /home/gigguide/backup/gigguide.sql
chown gigguide:gigguide /home/gigguide/backup/gigguide.sql

mkdir -p /var/log/gunicorn/
chown -R www:www-data /var/log/gunicorn/
chmod -R g+s /var/log/gunicorn/

mkdir -p /var/spacy/
chmod -R 770 /var/spacy/
chown -R gigguide:gigguide /var/spacy/
'''