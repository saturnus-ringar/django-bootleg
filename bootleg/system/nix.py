import getpass
import grp
import os
import pwd

from bootleg.system.shell import run_command

from bootleg.system import shell
from bootleg.conf import bootleg_settings
from django.conf import settings


def get_alias_prefix():
    if getattr(bootleg_settings, "ALIAS_PREFIX", None):
        return bootleg_settings.ALIAS_PREFIX

    return bootleg_settings.PROJECT_NAME


def setup_alias_file():
    content = "# !/bin/bash\n"
    content += 'SOURCE_ENV = "source /home/%s/env/bin/activate"\n' % bootleg_settings.PROJECT_NAME
    content += 'PROJECT_PATH = "source /home/%s/env/bin/activate"\n' % bootleg_settings.PROJECT_NAME
    content += 'LOG_DIR = "%s"\n' % settings.LOG_DIR
    content += 'alias pm="python manage.py"\n'
    content += 'alias %s="$SOURCE_ENV; cd $PROJECT_PATH"\n' % get_alias_prefix()
    content += 'alias %sdeploy="$SOURCE_ENV; cd $PROJECT_PATH; pm deploy"\n' % get_alias_prefix()
    content += 'alias %ssoftdeploy="$SOURCE_ENV; cd $PROJECT_PATH; pm deploy -s"\n' % get_alias_prefix()
    content += 'alias %stail="tail -f ${LOG_DIR}debug/debug.log"\n' % get_alias_prefix()
    filename = os.path.expanduser('~') + "/alias.sh"
    f = open(filename, "w")
    f.write(content)
    f.close()
    run_command(["chmod", "+x", filename])


def is_current_user(user):
    if getpass.getuser() != user:
        return False

    return True


def get_user_groups(user):
    groups = [g.gr_name for g in grp.getgrall() if user in g.gr_mem]
    try:
        gid = pwd.getpwnam(user).pw_gid
        groups.append(grp.getgrgid(gid).gr_name)
    except KeyError:
        pass
    return groups


def user_is_in_group(user, group):
    if group in get_user_groups(user):
        return True

    return False


def user_exists(user):
    try:
        pwd.getpwnam(user)
        return True
    except KeyError:
        return False


def group_exists(group):
    try:
        grp.getgrnam(group)
        return True
    except KeyError:
        return False


def get_sar_file_path(filename):
    return os.path.dirname(__file__) + "/dev_data/%s" % filename


def get_ubuntu_information():
    try:
        return shell.run_command(["lsb_release", "-a"])
    except:
        pass
