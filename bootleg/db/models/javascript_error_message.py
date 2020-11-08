from django.db import models
from django.utils.translation import ugettext as _


class JavascriptErrorMessage(models.Model):
    message = models.CharField(blank=False, null=False, max_length=8192)

    def __str__(self):
        return self.message

    class Meta:
        verbose_name = _("Javascript-error-message")
        verbose_name_plural = _("Javascript-error-messages")
