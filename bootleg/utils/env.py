import os
import sys

from bootleg.system.shell import run_command
from django.conf import settings


def is_testing():
    if sys.argv[1:2] == ['test']:
        return True

    return False


def is_apache():
    if "APACHE_PID_FILE" in os.environ:
        return True
    return False


def is_gunicorn():
    if "gunicorn" in os.environ.get("SERVER_SOFTWARE", ""):
        return True

    return False


def check_if_service_is_running(service_name):
    try:
        output = run_command(["systemctl", "is-active", service_name])
        if "inactive" not in output:
            return True
        return False
    except FileNotFoundError:
        return False


def is_apache_from_cli():
    return check_if_service_is_running("apache2")


def is_gunicorn_from_cli():
    return check_if_service_is_running("gunicorn")


def is_production():
    if getattr(settings, "DEBUG"):
        if is_apache():
            return True

        if is_gunicorn():
            return True

    return False


def is_github():
    if "GITHUB_ACTIONS" in os.environ:
        return True

    return False


# https://stackoverflow.com/a/42580137
def is_venv():
    return (hasattr(sys, 'real_prefix') or
            (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix))
