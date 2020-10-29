import logging
import os
import traceback
import warnings
from pathlib import Path

from bootleg.conf import settings
from bootleg.utils import utils, file_system
from bootleg.utils.file_system import NotWritableWarning


class StreamHandler(logging.StreamHandler):

    def emit(self, record):
        if utils.is_apache_context():
            # don't log in apache context
            return
        super().emit(record)


class FileHandler(logging.FileHandler):

    def __init__(self, filename, mode='a', encoding=None, delay=0):
        writable = True
        encoding = "utf-8"

        try:
            file_system.mkdir_p(os.path.dirname(filename))
        except PermissionError:
            writable = False
        try:
            Path(filename).touch()
        except (FileNotFoundError, PermissionError):
            writable = False

        if not writable:
            warnings.warn('File path %s is not writable. Logging to: %s instead.' % (filename, settings.fail_log_path()),
                          NotWritableWarning, stacklevel=3)
            filename = settings.fail_log_path()

        logging.FileHandler.__init__(self, filename, mode, encoding, delay)


class DjangoLogHandler(FileHandler):
    levels = ["WARNING", "ERROR", "CRITICAL"]

    def should_log(self, record):
        if settings.store_django_log_exceptions() and record.levelname in self.levels:
            return True

        return False

    def emit(self, record):
        if self.should_log(record):
            self.create_entry(record)
        super().emit(record)

    def create_entry(self, record):
        # have to import here, the apps are not loaded on the initial import of this file
        from bootleg.db.models.django_log_entry import DjangoLogEntry
        clazz = "UnknownClass"
        try:
            clazz = str(record.exc_info[0].__name__)
        except:
            # not sure why this is happening but record.exc_info[0] seems empty sometimes
            pass

        if record.filename != "basehttp.py" and clazz != "UnknownClass":
            # seems pointless logging these basehttp-thingies, I'm not sure what it is but the stack trace is empty.
            # ... and they are triggered on every exception
            DjangoLogEntry.objects.create(record.levelname, clazz, traceback.format_exc(), record.filename,
                                          record.args)
