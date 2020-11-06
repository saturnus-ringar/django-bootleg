import os
import sys
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


def is_production():
    if getattr(settings, "DEBUG"):
        if is_apache():
            return True

        if is_gunicorn():
            return True

    return False


def is_github():
    dx("***************************************************************************")
    dx("is_github")
    dx(os.environ)
    if "GITHUB_ACTIONS" in os.environ:
        dx("True")
        return True

    dx("False")
    return False
