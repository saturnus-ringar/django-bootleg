from django.utils.translation import ugettext as _

from bootleg.db.models.base import ExceptionModel


class LoggedException(ExceptionModel):

    def __str__(self):
        return _("Logged exception %s" % str(self.id))

    class Meta:
        verbose_name = _("Logged exception")
        verbose_name_plural = _("Logged exceptions")
