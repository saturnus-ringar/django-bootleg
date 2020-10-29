from django.core.exceptions import ValidationError
from django.core.validators import URLValidator


def is_valid_url(url):
    try:
        URLValidator(url)
    except ValidationError:
        return False
