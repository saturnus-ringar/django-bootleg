import inspect
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


def is_gunicorn_context():
    if "gunicorn" in os.environ.get("SERVER_SOFTWARE", ""):
        return True

    return False


def get_caller():
    stack = inspect.stack()
    if "self" in stack[2][0].f_locals:
        the_class = stack[2][0].f_locals["self"].__class__
        the_method = stack[2][0].f_code.co_name
        # returns "dev.Command.method()" from. "core.management.commands.dev.Command"
        return str(the_class).split(".")[-2] + "." + str(the_class).split(".")[-1][:-2] + "." + str(the_method) + "()"
    else:
        # a function is calling
        return str(stack[2][0].f_code.co_name)


# https://stackoverflow.com/a/58045927/7903576
def get_full_class_name(obj):
    module = obj.__class__.__module__
    if module is None or module == str.__class__.__module__:
        return obj.__class__.__name__
    return module + '.' + obj.__class__.__name__
