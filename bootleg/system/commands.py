import os
from shutil import which

from bootleg.system import shell
from bootleg.system.shell import run_command


SAR_COMMAND_EXISTS = which("sar") is not None


def get_sar_file_path(filename):
    return os.path.dirname(__file__) + "/dev_data/%s" % filename


def get_dir_size_h(dir):
    return run_command(["du", "-h", dir])


def get_disk_usage_h():
    return run_command(["df", "-h"])


def get_disk_usage():
    return run_command(["df"])


def get_sar_command(command, filename):
    if not SAR_COMMAND_EXISTS:
        with open(get_sar_file_path(filename), 'r') as file:
            return file.read()
    else:
        return run_command(command)


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


def get_load_average_cleaned():
    return shell.output_to_list_and_ignore_string(get_load_average(), "ldavg-15",
                                                                lines_to_ignore=[0])


def get_memory_usage_cleaned():
    return shell.output_to_list_and_ignore_string(get_memory_usage(), "kbmemfree",
                                                                lines_to_ignore=[0])
