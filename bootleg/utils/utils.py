import importlib
import inspect


def get_meta_class_value(clazz, value):
    if hasattr(clazz, "_meta"):
        if hasattr(clazz._meta, value):
            return getattr(clazz._meta, value)
    elif hasattr(clazz.Meta, value):
        return getattr(clazz.Meta, value)
    return None


def get_class(module, clazz):
    my_module = importlib.import_module(module)
    return getattr(my_module, clazz)


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
