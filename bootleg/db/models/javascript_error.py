from bootleg.logging import logging

from bootleg.db.models.base import HandledStatusModel
from django.db import models
from django_extensions.db.models import TimeStampedModel

from bootleg.db.models.javascript_error_message import JavascriptErrorMessage
from django.utils.translation import ugettext as _


class JavascriptErrorManager(models.Manager):

    def create(self, ip, message, url, line):
        javascript_error_message = JavascriptErrorMessage.objects.filter(message=message).first()
        if not javascript_error_message:
            # create a new javascript error message then
            javascript_error_message = JavascriptErrorMessage()
            javascript_error_message.message = message
            javascript_error_message.save()

        javascript_error = JavascriptError()
        javascript_error.message = javascript_error_message
        javascript_error.ip = ip
        javascript_error.url = url
        javascript_error.line = line
        javascript_error.save()


class JavascriptError(HandledStatusModel):
    ip = models.GenericIPAddressField(null=False, blank=False)
    url = models.URLField(null=False, blank=False)
    line = models.IntegerField(null=False, blank=False)
    message = models.ForeignKey(JavascriptErrorMessage, null=False, blank=False, on_delete=models.CASCADE)

    objects = JavascriptErrorManager()

    def handle(self, request):
        self.handled = True
        self.save()
        logging.log_audit(logging.HANDLED + " the javascript error with id: [%s]" % self.id, request)

    def __str__(self):
        return self.message.message + " " + str(self.line)

    class Meta:
        verbose_name = _("Javascript-error")
        verbose_name_plural = _("Javascript-errors")
