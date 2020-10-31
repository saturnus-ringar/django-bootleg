import getpass
import grp
import os
import pwd

from bootleg.system import shell
from bootleg.system.shell import run_command


def get_ubuntu_information():
    try:
        return run_command(["lsb_release", "-a"])
    except:
        pass


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
