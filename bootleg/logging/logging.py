import builtins
import logging
import sys
import traceback
from pathlib import Path
from pprint import pformat

from django.conf import settings as django_settings
from ipware import get_client_ip

from bootleg.conf import settings
from bootleg.logging.handlers import StreamHandler, FileHandler
from bootleg.utils import utils, file_system

CREATED = "CREATED"
UPDATED = "UPDATED"
HANDLED = "HANDLED"

LOGGERS = {}
LOG_DIR_IS_WRITABLE = file_system.is_writable(settings.log_dir())


def get_log_level(filename):
    level = settings.log_level()
    if filename == "debug":
        # always debug, in the debug log
        level = "DEBUG"
    return level


def get_logger(filename):
    if not LOG_DIR_IS_WRITABLE:
        return None

    logger = None

    if filename in LOGGERS:
        logger = LOGGERS[filename]

    if not logger:
        # create the logger then
        level = get_log_level(filename)
        file_path = get_file_path(filename)

        try:
            Path(file_path).touch()
        except (FileNotFoundError, PermissionError):
            # not writable, warn and go for dev null
            file_path = settings.fail_log_path()

        logger = logging.getLogger(filename)
        logger.setLevel(level)
        # add custom file handler
        handler = FileHandler(file_path)
        handler.setLevel(level)
        handler.setFormatter(get_formatter())
        logger.addHandler(handler)
        if settings.log_to_stdout():
            # add stream handler ... indeed
            add_stream_handler(logger)

        LOGGERS[filename] = logger

    if len(logger.handlers) > 2:
        # there are some race conditions where multiple handlers are added, fix the handlers
        logger.handlers = fix_log_handlers(logger.handlers)

    return logger


def fix_log_handlers(handlers):
    fixed_handlers = []
    file_handler_added = False
    stream_handler_added = False
    for handler in handlers:
        if not file_handler_added and isinstance(handler, FileHandler):
            fixed_handlers.append(handler)
            file_handler_added = True
        if not stream_handler_added and isinstance(handler, StreamHandler):
            fixed_handlers.append(handler)
            stream_handler_added = True

    return fixed_handlers


def add_stream_handler(logger):
    stream_handler = StreamHandler(sys.stdout)
    stream_handler.setFormatter(get_formatter())
    stream_handler.setLevel(settings.log_level())
    logger.addHandler(stream_handler)


def get_file_path(filename):
    if not filename.endswith(".log"):
        filename = filename + ".log"

    return settings.log_dir() + filename


def get_formatter():
    try:
        return logging.Formatter(django_settings.LOGGING["formatters"]["verbose"]["format"],
                                 django_settings.LOGGING["formatters"]["verbose"]["datefmt"])
    except KeyError:
        return logging.Formatter()


def log_exception(e):
    if settings.store_logged_exception():
        save_logged_exception(e)


def save_logged_exception(e):
    # have to import here, the apps are not loaded on the initial import of this file
    from bootleg.db.models.logged_exception import LoggedException
    LoggedException.objects.create(utils.get_full_class_name(e), traceback.format_exc(), str(e.args)[:1024])


def debug(msg):
    get_logger("debug").debug(msg)


def log_audit(message, request=None):
    if request:
        get_logger("audit").info(get_ip_to_log(request) + get_user_to_log(request.user) + message)
    else:
        get_logger("audit").info(message)


def get_ip_to_log(request):
    ip, routable = get_client_ip(request)
    return "IP: [%s] " % ip


def get_user_to_log(user):
    return "User: [%s] " % user.username


def add_builtins():
    # hack, hack..... .... ... .. .!

    def dx(obj, verbose=False):
        if verbose:
            debug("Class: %s Base class: %s" % (obj.__class__.__name__, obj.__class__.__bases__))
            debug("dir: %s" % dir(obj))

        debug(pformat(obj))

    def dxv(obj):
        dx(obj, True)

    builtins.dx = dx
    builtins.dxv = dxv
