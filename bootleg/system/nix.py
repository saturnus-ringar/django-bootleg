import getpass
import grp
import pwd
from shutil import which

from bootleg.system.shell import run_command

from bootleg.system import shell

SAR_COMMAND_EXISTS = which("sar") is not None


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


def get_dir_size_h(dir):
    return shell.run_command(["du", "-h", dir])


def get_disk_usage_h():
    return shell.run_command(["df", "-h"])


def get_disk_usage():
    return shell.run_command(["df"])


def get_sar_command(command, filename):
    if not SAR_COMMAND_EXISTS:
        with open(get_sar_file_path(filename), 'r') as file:
            return file.read()
    else:
        return shell.run_command(command)


def get_load_average():
    return get_sar_command(["sar", "-q"], "sar_q_output.txt")


def get_disk_io():
    return get_sar_command(["sar", "-d"], "sar_d_output.txt")


def get_cpu_usage():
    return get_sar_command(["sar"], "sar_output.txt")


def get_memory_usage():
    return get_sar_command(["sar", "-r"], "sar_q_output.txt")


def get_memory_usage_h():
    return get_sar_command(["sar", "-rh"], "sar_rh_output.txt")


def shell_output_to_list_and_ignore_string(output, string, lines_to_ignore=None):
    cleaned_data = []
    for row in shell.output_to_list(output, lines_to_ignore):
        if row and string not in row:
            cleaned_data.append(row)

    return cleaned_data


def get_load_average_cleaned():
    return shell_output_to_list_and_ignore_string(get_load_average(), "ldavg-15",
                                                                lines_to_ignore=[0])


def get_memory_usage_cleaned():
    return shell_output_to_list_and_ignore_string(get_memory_usage(), "kbmemfree",
                                                                lines_to_ignore=[0])
