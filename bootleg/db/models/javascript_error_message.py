from bootleg.logging import logging
from django.db import models
from django.utils.translation import ugettext as _


class JavascriptErrorMessage(models.Model):
    message = models.CharField(blank=False, null=False, max_length=8192)

    def handle(self, request):
        self.handled = True
        self.save()
        logging.log_audit(logging.HANDLED + " the javascript error with id: [%s]" % self.id, request)

    def __str__(self):
        return self.message

    class Meta:
        verbose_name = _("Javascript-error-message")
        verbose_name_plural = _("Javascript-error-messages")
