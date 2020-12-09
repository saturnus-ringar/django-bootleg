import getpass
import grp
import os
import pwd

from django.conf import settings

from bootleg.conf import bootleg_settings
from bootleg.logging.logging import bootleg_debug_log
from bootleg.system import shell
from bootleg.system.file_system import write_file
from bootleg.system.shell import run_command
from bootleg.utils.env import get_virtual_env_dir


def get_alias_prefix():
    if getattr(bootleg_settings, "PROJECT_ABBR", None):
        return bootleg_settings.PROJECT_ABBR

    return bootleg_settings.PROJECT_NAME


def get_home_directory_of_main_user():
    mac_os_dir = "/Users/%s/" % bootleg_settings.MAIN_USER
    if os.path.isdir(mac_os_dir):
        return mac_os_dir

    nix_dir = "/home/%s/" % bootleg_settings.MAIN_USER
    if os.path.isdir(nix_dir):
        return nix_dir


def setup_alias_file():
    home_dir = get_home_directory_of_main_user()
    if home_dir:
        bootleg_debug_log("writing alias file with virtual env: [%s] alias prefix: [%s]"
                          % (get_virtual_env_dir(), get_alias_prefix()))
        content = "# !/bin/bash\n"
        content += 'SOURCE_ENV="source %sbin/activate"\n' % get_virtual_env_dir()
        content += 'PROJECT_DIR="%s"\n' % settings.BASE_DIR
        content += 'LOG_DIR="%s"\n' % settings.LOG_DIR
        content += 'alias pm="python manage.py"\n'
        content += 'alias %s="$SOURCE_ENV; cd $PROJECT_DIR"\n' % get_alias_prefix()
        content += 'alias %spm="%s; python manage.py"\n' % (get_alias_prefix(), get_alias_prefix())
        content += 'alias %sdeploy="%s; pm deploy"\n' % (get_alias_prefix(), get_alias_prefix())
        content += 'alias %ssoftdeploy="%s; pm deploy -s"\n' % (get_alias_prefix(), get_alias_prefix())
        content += 'alias %srun="%s; pm runserver"\n' % (get_alias_prefix(), get_alias_prefix())
        # log aliases
        content += 'alias %slogdir="cd $LOG_DIR"\n' % get_alias_prefix()
        content += 'alias %stail="tail -f ${LOG_DIR}debug.log"\n' % get_alias_prefix()
        content += 'alias %stailaccess="tail -f ${LOG_DIR}access.log"\n' % get_alias_prefix()
        content += 'alias %staildjango="tail -f ${LOG_DIR}access.log"\n' % get_alias_prefix()
        content += 'alias %scleardebug="cat /dev/null > ${LOG_DIR}debug.log"\n' % get_alias_prefix()
        content += 'alias %sviewdebuglog="less ${LOG_DIR}debug.log"\n' % get_alias_prefix()
        content += 'alias %sstatus="%s; pm status"\n' % (get_alias_prefix(), get_alias_prefix())
        content += 'alias %scmd="%s; pm cmd"\n' % (get_alias_prefix(), get_alias_prefix())
        # well... write file then
        filename = "%saliases_%s.sh" % (home_dir, bootleg_settings.PROJECT_NAME)
        write_file(filename, content)
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
