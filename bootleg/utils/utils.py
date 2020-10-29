import os
import sys


def is_testing():
    if sys.argv[1:2] == ['test']:
        return True

    return False


def is_apache_context():
    if "APACHE_PID_FILE" in os.environ:
        return True
    return False


# https://stackoverflow.com/a/58045927/7903576
def get_full_class_name(obj):
    module = obj.__class__.__module__
    if module is None or module == str.__class__.__module__:
        return obj.__class__.__name__
    return module + '.' + obj.__class__.__name__
