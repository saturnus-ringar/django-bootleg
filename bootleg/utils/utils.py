import importlib
import inspect
from io import StringIO

from django.core.handlers.wsgi import WSGIRequest


class Singleton:

    instance = None

    def __new__(cls):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance


# https://gist.github.com/majgis/4164503
def get_fake_request(path="/", user=None):
    from bootleg.utils import models
    from django.contrib.auth.models import AnonymousUser
    req = WSGIRequest({
          'REQUEST_METHOD': 'GET',
          'PATH_INFO': path,
          'wsgi.input': StringIO()})
    req.user = AnonymousUser() if user is None else user
    req.editable_models = models.get_editable_models_dict()
    return req


# there are probably easier ways of doing this?!
def get_attr__(obj, attr):
    attrs = attr.split("__")
    if len(attrs) > 1:
        if hasattr(obj, attrs[0]):
            main_attr = getattr(obj, attrs[0])
            if hasattr(main_attr, attrs[1]):
                return getattr(main_attr, attrs[1])
    else:
        if hasattr(obj, attr):
            return getattr(obj, attr)

    return None


def get_meta_class_value(clazz, value):
    if hasattr(clazz, "_meta"):
        if hasattr(clazz._meta, value):
            return getattr(clazz._meta, value)
    elif hasattr(clazz.Meta, value):
        return getattr(clazz.Meta, value)
    return None


def meta_class_value_is_true(clazz, value):
    value = get_meta_class_value(clazz, value)
    if value and value is True:
        return True

    return False


def get_class(module, clazz):
    return getattr(importlib.import_module(module), clazz)


def get_non_abstract_subclasses(klazz):
    klazzes = []
    for inheritor in get_subclasses(klazz):
        if not hasattr(inheritor.Meta, "abstract") or not inheritor.Meta.abstract:
            klazzes.append(inheritor)
    klazzes.sort(key=lambda x: x.__name__)
    return klazzes


def get_subclasses(klass):
    # this only works if the classes are in the same python file, it seems
    subclasses = []
    work = [klass]
    while work:
        parent = work.pop()
        for child in parent.__subclasses__():
            if child not in subclasses:
                subclasses.append(child)
                work.append(child)
    return subclasses


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
