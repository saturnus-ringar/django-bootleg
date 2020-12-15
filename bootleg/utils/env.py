import os
import sys

from bootleg.system.shell import run_command
from django.conf import settings
from bootleg.conf import bootleg_settings


def is_testing():
    if sys.argv[1:2] == ['test']:
        return True

    return False


def is_manage():
    if sys.argv[0] == 'manage.py':
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


def is_apache_from_cli():
    return service_is_running("apache2")


def is_gunicorn_from_cli():
    return service_is_running("gunicorn")


def service_is_running(service_name):
    try:
        output = run_command(["systemctl", "is-active", service_name])
        if "inactive" not in output:
            return True
        return False
    except FileNotFoundError:
        return False


def is_production():
    if settings.DEBUG is False:
        if is_apache():
            return True
        elif is_gunicorn():
            return True

    return False


def is_github():
    if "GITHUB_ACTIONS" in os.environ:
        return True

    return False


def use_elastic_search():
    if bootleg_settings.DISABLE_ELASTIC_SEARCH is True:
        return False

    return True

# https://stackoverflow.com/a/42580137
def is_venv():
    return (hasattr(sys, 'real_prefix') or
            (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix))


def get_virtual_env_dir():
    # haven't figured out any good way of getting this :|, os.environ["VIRTUAL_ENV"] is not
    # available when running in Apache-context
    return sys.executable.replace("bin/python", "")
