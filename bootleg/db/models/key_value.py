from annoying.functions import get_object_or_None
from django.conf import settings
from django.db import models
from django.utils import dateformat, dateparse
from django.utils.translation import ugettext as _

from bootleg.db.models.base import BaseModel
import dateutil.parser


class KeyValueManger(models.Manager):

    def set(self, key, value):
        key_value = get_object_or_None(KeyValue, key=key)
        if not key_value:
            key_value = KeyValue()

        key_value.key = key
        key_value.value = value
        key_value.save()

    def get_int(self, key, default=0):
        key_value = get_object_or_None(KeyValue, key=key)
        if key_value:
            return int(key_value.value)

        return default

    def set_datetime(self, key, datetime):
        self.set(key, dateformat.format(datetime, settings.DATETIME_FORMAT))

    def get_datetime(self, key):
        key_value = get_object_or_None(KeyValue, key=key)
        if key_value:
            return dateutil.parser.parse(key_value.value)
        return None


class KeyValue(BaseModel):
    key = models.CharField(max_length=254, unique=True, db_index=True)
    value = models.CharField(max_length=1024)

    objects = KeyValueManger()

    def __str__(self):
        return self.key + " - " + self.value

    class Meta:
        verbose_name = _("Key value")
        verbose_name_plural = _("Key values")
