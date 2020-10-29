import base64
import zlib

from django.db import models


# compression based on
# https://medium.com/@busybus/zipjson-3ed15f8ea85d

class CompressedTextField(models.TextField):

    def from_db_value(self, value, expression, connection):
        return zlib.decompress(base64.b64decode(value))

    def to_python(self, value):
        return base64.b64encode(zlib.compress(value.encode('utf-8'))).decode('ascii')
