import builtins
import logging
import os
import sys
import traceback
import warnings
from pprint import pformat

from ipware import get_client_ip

from bootleg.conf import bootleg_settings
from bootleg.conf.settings import check_log_level
from bootleg.logging.handlers import StreamHandler, FileHandler
from bootleg.settings import LOG_FORMAT, LOG_DATE_FORMAT
from bootleg.system import file_system
from bootleg.system.file_system import NotWritableWarning
from bootleg.utils import utils

CREATED = "CREATED"
UPDATED = "UPDATED"
HANDLED = "HANDLED"

LOGGERS = {}
DEBUG_LOGGER = []

LOG_DIR_IS_WRITABLE = file_system.is_writable(bootleg_settings.LOG_DIR)


class LogFilenameException(Exception):
    pass


def get_all_loggers():
    loggers_with_handlers = []
    loggers_without_handlers = []

    for logger_name in sorted(logging.root.manager.loggerDict):
        logger = logging.getLogger(logger_name)
        if logger.handlers:
            loggers_with_handlers.append(logger)
        else:
            loggers_without_handlers.append(logger)

    return loggers_with_handlers + loggers_without_handlers


def test_writing_and_get_filename(filename):
    writable = True
    try:
        file_system.mkdir_p(os.path.dirname(filename))
    except PermissionError:
        writable = False

    if not writable:
        warnings.warn('File path %s is not writable.' % filename,
                      NotWritableWarning, stacklevel=3)

    return filename


def get_log_level(filename):
    level = bootleg_settings.LOG_LEVEL
    if filename == "debug":
        # always debug, in the debug log
        level = "DEBUG"
    return level


def get_logger(filename):
    extension = os.path.splitext(filename)[1]
    if extension:
        raise LogFilenameException("The filename should not contain an extension. Just 'path/file'.")
    if not LOG_DIR_IS_WRITABLE:
        return None

    logger = None

    if filename in LOGGERS:
        logger = LOGGERS[filename]

    if not logger:
        # create the logger then
        level = get_log_level(filename)
        file_path = get_file_path(filename)
        file_path = test_writing_and_get_filename(file_path)
        logger = logging.getLogger(filename)
        check_log_level(level)
        logger.setLevel(level)
        # add custom file handler
        handler = FileHandler(file_path)
        handler.setLevel(level)
        handler.setFormatter(get_formatter())
        logger.addHandler(handler)
        if bootleg_settings.LOG_TO_STDOUT:
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
    stream_handler.setLevel(bootleg_settings.LOG_LEVEL)
    logger.addHandler(stream_handler)


def get_file_path(filename):
    if not filename.endswith(".log"):
        filename = filename + ".log"

    return bootleg_settings.LOG_DIR + filename


def get_formatter():
    return logging.Formatter(LOG_FORMAT, LOG_DATE_FORMAT)


def log_exception(e):
    logger = get_logger("exception")
    logger.exception(e)
    if bootleg_settings.STORE_LOGGED_EXCEPTIONS:
        save_logged_exception(e)


def save_logged_exception(e):
    # have to import here, the apps are not loaded on the initial import of this file
    from bootleg.db.models.logged_exception import LoggedException
    LoggedException.objects.create(utils.get_full_class_name(e), traceback.format_exc(), str(e.args)[:1024])


def debug_log(msg):
    if DEBUG_LOGGER:
        logger = DEBUG_LOGGER
    else:
        logger = get_logger("debug")

    logger.debug(msg)


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
            debug_log("Class: %s Base class: %s" % (obj.__class__.__name__, obj.__class__.__bases__))
            debug_log("dir: %s" % dir(obj))

        debug_log(pformat(obj))

    def dxv(obj):
        dx(obj, True)

    def dp(obj, verbose=False):
        dx(obj, verbose)


    builtins.dp = dp
    builtins.dx = dx
    builtins.dxv = dxv
