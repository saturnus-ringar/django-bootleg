from django.conf import settings
from bootleg.conf import bootleg_settings
from bootleg.db.models.django_log_entry import DjangoLogEntry
from bootleg.db.models.logged_exception import LoggedException
from bootleg.utils import models


def globals(request):
    editable_models = None
    unhandled_logged_exceptions_count = None
    unhandled_django_log_entry_count = None

    if request.user.is_staff:
        editable_models = models.get_editable_models_dict()
        unhandled_logged_exceptions_count = LoggedException.unhandled.all().count()
        unhandled_django_log_entry_count = DjangoLogEntry.unhandled.all().count()

    request.editable_models = editable_models
    request.unhandled_logged_exceptions_count = unhandled_logged_exceptions_count
    request.unhandled_django_log_entry_count = unhandled_django_log_entry_count

    return {
        "editable_models": editable_models,
        "unhandled_logged_exceptions_count": unhandled_logged_exceptions_count,
        "unhandled_django_log_entry_count": unhandled_django_log_entry_count,
        "settings": settings,
        "bootleg_settings": bootleg_settings,
    }
