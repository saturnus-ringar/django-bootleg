import os
import platform
import sys
from collections import OrderedDict

import django

from bootleg.system.shell import CommandException
from bootleg.utils.env import get_virtual_env_dir

if django.VERSION >= (3, 1):
    from django.views.debug import get_default_exception_reporter_filter
    cleanse_setting = get_default_exception_reporter_filter().cleanse_setting
else:
    from django.views.debug import cleanse_setting

import bootleg
import pkg_resources
from debug_toolbar.panels.settings import get_safe_settings
from django.conf import settings
from django.db import connection, OperationalError

from bootleg.db import db
from bootleg.logging import logging
from bootleg.system import shell, file_system, commands, nix
from bootleg.utils import humanize, env


class Disk:

    def __init__(self, mount, size, used):
        self.mount = mount
        self.size = size
        self.used = used

    def get_free(self):
        return int(self.size) - int(self.used)

    def __str__(self):
        return "Mount: %s Size: %s Used: %s" % (self.mount, self.size, self.used)


class System:

    def __init__(self):
        # os/platform
        self.platform = self.get_platform()
        self.ubuntu_information = nix.get_ubuntu_information()
        # python ...stuff...
        self.python_version = self.cleanup(sys.version)
        self.executable = sys.executable
        self.virtual_env_path = get_virtual_env_dir()

        # system stats
        self.uptime = shell.run_command(["uptime"])
        self.disk_usage = commands.get_disk_usage_h()
        self.disks = self.get_disks()

        # sar data
        self.set_sar_data()

        # installed packages
        self.installed_packages = self.get_installed_packages()

        # directories
        self.project_path = self.get_project_path()
        self.media_root = getattr(settings, "MEDIA_ROOT")
        self.static_root = getattr(settings, "STATIC_ROOT")
        self.project_dir_last_modified_file = file_system.get_last_modified_file(self.project_path)
        self.env_dir_last_modified_file = file_system.get_last_modified_file(self.virtual_env_path)
        self.media_dir_last_modified_file = file_system.get_last_modified_file(getattr(settings, "MEDIA_ROOT"))
        self.static_dir_last_modified_file = file_system.get_last_modified_file(getattr(settings, "STATIC_ROOT"))
        self.bootleg_version = bootleg.__version__
        self.django_version = django.get_version()
        self.env = self.get_env()

        # log dirs
        if os.getenv("APACHE_LOG_DIR"):
            self.apache_log_dir_info = commands.get_dir_size_h(os.getenv("APACHE_LOG_DIR")).strip()
        self.log_dir_info = commands.get_dir_size_h(getattr(settings, "LOG_DIR"))

        # mysql-info
        self.mysql_version = self.get_mysql_version()
        self.mysql_table_status = self.get_mysql_table_status_filtered()
        self.db_size = self.get_db_size()
        # loggers
        self.loggers = logging.get_all_loggers()

        # django settings (using django debug toolbar)
        self.django_settings = OrderedDict(sorted(get_safe_settings().items(), key=lambda s: s[0]))

    def set_sar_data(self):
        sar_failure = "sar command failed"
        try:
            self.memory_usage = commands.get_memory_usage_h()
        except CommandException:
            self.memory_usage = sar_failure

        try:
            self.load_average = commands.get_load_average()
        except CommandException:
            self.load_average = sar_failure

        try:
            self.cpu_usage = commands.get_cpu_usage()
        except CommandException:
            self.cpu_usage = sar_failure

        try:
            self.disk_io = commands.get_disk_io()
        except CommandException:
            self.disk_io = sar_failure

        # not used atm.
        #self.load_average_data = commands.get_load_average_cleaned()
        #self.memory_usage_data = commands.get_memory_usage_cleaned()

    def get_short_python_version(self):
        return self.python_version.split()[0]

    def get_env(self):
        cleaned_env = []
        for key, value in sorted(os.environ.items()):
            env = {}
            env["key"] = key
            env["value"] = cleanse_setting(key.upper(), value)
            cleaned_env.append(env)

        return cleaned_env

    def get_linux_distribution_formatted(self):
        return " ".join(self.linux_distribution).strip()

    def get_disks(self):
        # du-output
        # Filesystem    512 - blocks    Used        Available   Capacity    iused   ifree       %iused  Mounted on
        # /dev/disk1s5  1953115488      22185656    269243200   8%          488746  9765088694  0%      /
        disks = []
        disks_to_check = getattr(settings, "DISKS_TO_CHECK", None)
        if disks_to_check:
            for data in shell.output_to_list(commands.get_disk_usage(), lines_to_ignore=[0]):
                if data[0] in disks_to_check:
                    disks.append(Disk(data[0], data[1], data[2]))
            return disks

    def get_platform(self):
        return platform.system() + " " + platform.release() + " " + platform.version()

    def get_mysql_table_status_filtered(self):
        data = self.get_mysql_table_status()
        cleaned_data = []

        if data:
            for row in data:
                clean_row = {}
                clean_row["Name"] = row["Name"]
                clean_row["Engine"] = row["Engine"]
                clean_row["Rows"] = row["Rows"]
                clean_row["Data size"] = humanize.humanize_bytes(row["Data_length"])
                clean_row["Index size"] = humanize.humanize_bytes(row["Data_length"])
                clean_row["Total size"] = humanize.humanize_bytes(row["Data_length"] + row["Index_length"])
                cleaned_data.append(clean_row)

        return cleaned_data

    def get_mysql_table_status(self):
        if env.is_mysql():
            with connection.cursor() as cursor:
                cursor.execute("SHOW TABLE STATUS")
                return db.dictfetchall(cursor)
        return None

    def get_mysql_version(self):
        if env.is_mysql():
            with connection.cursor() as cursor:
                cursor.execute("SELECT VERSION()")
                row = cursor.fetchone()
            return "MySQL %s" % row

        return None

    def get_db_size(self):
        if env.is_mysql():
            with connection.cursor() as cursor:
                cursor.execute("SELECT sum(round(data_length + index_length)) as 'bytes' FROM "
                               "information_schema.TABLES WHERE table_schema = '%s'" %
                               getattr(settings, "DATABASES")["default"]["NAME"])
                return int(cursor.fetchone()[0])

        return None

    # this doesn't work very well on large tables, it seems
    def get_number_of_db_rows(self):
        if env.is_mysql():
            with connection.cursor() as cursor:
                cursor.execute("SELECT SUM(TABLE_ROWS) FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = '%s'" %
                               getattr(settings, "DATABASES")["default"]["NAME"])
                return int(cursor.fetchone()[0])

        return None

    def get_project_path(self):
        try:
            return getattr(settings, "BASE_DIR")
        except:
            return None

    def get_installed_packages(self):
        return reversed([d for d in pkg_resources.working_set])

    def cleanup(self, string):
        return string.replace("\n", " ")

    def __str__(self):
        return self.platform
