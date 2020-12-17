import re

from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _

from bootleg.conf import bootleg_settings
from bootleg.utils.models import display_model_in_menu


def strip_tags(html):
    return re.sub('<[^<]+?>', '', html)


def get_default_table_class_string():
    return "table table-striped table-responsive table-hover w-100 d-block d-md-table"

