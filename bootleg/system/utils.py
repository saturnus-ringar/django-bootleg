from django.conf import settings
import subprocess

from bootleg.system.shell import run_command_with_pipe


def get_requirements_file_path():
    return getattr(settings, "BASE_DIR") + "/requirements.txt"


def pip_install():
    return run_command_with_pipe(["pip", "install", "-r", get_requirements_file_path()],
                                 ["grep", "-v", "Requirement already satisfied"])


def restart_service(service):
    return subprocess.check_call(["sudo", "systemctl", "restart", service])


def restart_gunicorn():
    return restart_service("gunicorn.socket")


def restart_apache():
    return restart_service("apache2.service")
