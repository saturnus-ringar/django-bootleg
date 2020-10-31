import os
import platform
import sys

import pkg_resources
from bootleg.utils import humanize, db, file_system
from django.conf import settings
from django.db import connection, OperationalError


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
        self.ubuntu_information = shell.get_ubuntu_information()
        # python ...stuff...
        self.python_version = self.cleanup(sys.version)
        self.executable = sys.executable
        self.virtual_env_path = self.get_virtual_env_path()

        # system stats
        self.disk_usage = shell.get_disk_usage_h()
        self.memory_usage = shell.get_memory_usage_h()
        self.load_average = shell.get_load_average()
        self.cpu_usage = shell.get_cpu_usage()
        self.disk_io = shell.get_disk_io()
        self.disks = self.get_disks()
        self.load_average_data = shell.get_load_average_cleaned()
        self.memory_usage_data = shell.get_memory_usage_cleaned()

        # installed packages
        self.installed_packages = self.get_installed_packages()

        # directories
        self.project_path = self.get_project_path()
        self.media_root = getattr(settings, "MEDIA_ROOT")
        self.static_root = getattr(settings, "STATIC_ROOT")
        self.project_dir_last_modified_file = file_system.get_last_modification_date(self.project_path)
        self.env_dir_last_modified_file = file_system.get_last_modification_date(self.virtual_env_path)
        self.media_dir_last_modified_file = file_system.get_last_modification_date(getattr(settings, "MEDIA_ROOT"))
        self.static_dir_last_modified_file = file_system.get_last_modification_date(getattr(settings, "STATIC_ROOT"))
        self.env = self.get_env()

        # log dirs
        if os.getenv("APACHE_LOG_DIR"):
            self.apache_log_dir_info = shell.get_dir_size_h(os.getenv("APACHE_LOG_DIR")).strip()
        self.log_dir_info = shell.get_dir_size_h(getattr(settings, "LOG_DIR"))

        # mysql-info
        self.mysql_version = self.get_mysql_version()
        self.mysql_table_status = self.get_mysql_table_status_filtered()
        self.db_size = self.get_db_size()

    def get_env(self):
        cleaned_env = []
        non_allowed_patterns = ["password", "key"]
        for key, value in sorted(os.environ.items()):
            env = {}
            env["key"] = key
            env["value"] = value
            for pattern in non_allowed_patterns:
                if pattern.lower() in key.lower():
                    env["value"] = "************"

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
            for data in shell.output_to_list(shell.get_disk_usage(), lines_to_ignore=[0]):
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
        try:
            with connection.cursor() as cursor:
                cursor.execute("SHOW TABLE STATUS")
                return db.dictfetchall(cursor)
        except OperationalError:
            return None

    def get_mysql_version(self):
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT VERSION()")
                row = cursor.fetchone()
            return "MySQL %s" % row
        except OperationalError:
            return None

    def get_db_size(self):
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT sum(round(data_length + index_length)) as 'bytes' FROM "
                               "information_schema.TABLES WHERE table_schema = '%s'" %
                               getattr(settings, "DATABASES")["default"]["NAME"])
                return int(cursor.fetchone()[0])
        except OperationalError:
            return None

    def get_project_path(self):
        try:
            return getattr(settings, "BASE_DIR")
        except:
            return None

    def get_installed_packages(self):
        return reversed([d for d in pkg_resources.working_set])

    def get_virtual_env_path(self):
        # haven't figured out any good way of getting this :|, os.environ["VIRTUAL_ENV"] is not
        # available when running in Apache-context
        return sys.executable.replace("bin/python", "")

    def cleanup(self, string):
        return string.replace("\n", " ")

    def __str__(self):
        return self.platform