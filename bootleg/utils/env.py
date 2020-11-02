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
