import logging
import traceback

from django.core.exceptions import AppRegistryNotReady
from django.db import OperationalError

from bootleg.utils import env


class StreamHandler(logging.StreamHandler):

    def emit(self, record):
        if env.is_apache():
            # don't log in apache context
            return
        super().emit(record)


class FileHandler(logging.FileHandler):

    def __init__(self, filename, mode='a', encoding=None, delay=0):
        encoding = "utf-8"
        logging.FileHandler.__init__(self, filename, mode, encoding, delay)


class DjangoLogHandler(FileHandler):
    levels = ["WARNING", "ERROR", "CRITICAL"]

    def should_log(self, record):
        # local import since the logger is added very early on in settings.py and it will lead to
        # some circular import mayhem
        from bootleg.conf import bootleg_settings
        if bootleg_settings.STORE_DJANGO_LOG_EXCEPTIONS and record.levelname in self.levels:
            return True

        return False

    def emit(self, record):
        if self.should_log(record):
            try:
                self.create_entry(record)
            except OperationalError:
                # the db might fail - just pass and log to the text file
                pass
        super().emit(record)

    def create_entry(self, record):
        # have to import here, the apps are not loaded on the initial import of this file
        try:
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
        except AppRegistryNotReady:
            pass
