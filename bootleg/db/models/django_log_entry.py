from django.db import models

from django.utils.translation import ugettext as _

from bootleg.db.models.base import ExceptionModel, UnhandledExceptionManager
from bootleg.db.models.klass import Class
from bootleg.db.models.log_level import LogLevel


class DjangoLogEntryManager(models.Manager):

    def create(self, log_level, clazz, traceback, filename, args):
        log_level, created = LogLevel.objects.get_or_create(name=log_level)
        clazz, created = Class.objects.get_or_create(name=clazz)
        django_log_entry = DjangoLogEntry()
        django_log_entry.stack_trace = traceback
        django_log_entry.log_level = log_level
        django_log_entry.clazz = clazz
        django_log_entry.filename = filename
        django_log_entry.args = args
        django_log_entry.save()


class DjangoLogEntry(ExceptionModel):
    filename = models.CharField(max_length=1024, null=False, blank=False)
    log_level = models.ForeignKey(LogLevel, on_delete=models.CASCADE)

    unhandled = UnhandledExceptionManager()
    objects = DjangoLogEntryManager()

    def __str__(self):
        return str(self.filename + " " + str(self.log_level))

    class Meta:
        verbose_name = _("Django-log-entry")
        verbose_name_plural = _("Django-log-entries")
