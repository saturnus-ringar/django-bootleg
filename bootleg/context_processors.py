from django.conf import settings
from bootleg.conf import bootleg_settings
from bootleg.db.models.django_log_entry import DjangoLogEntry
from bootleg.db.models.javascript_error import JavascriptError
from bootleg.db.models.logged_exception import LoggedException
from bootleg.utils import models


def globals(request):
    unhandled_logged_exceptions_count = None
    unhandled_django_log_entry_count = None
    unhandled_javascript_error_count = None

    editable_models = models.get_editable_models_dict()
    if request.user.is_staff:
        unhandled_logged_exceptions_count = LoggedException.unhandled.all().count()
        unhandled_django_log_entry_count = DjangoLogEntry.unhandled.all().count()
        unhandled_javascript_error_count = JavascriptError.unhandled.all().count()

    request.editable_models = models.get_editable_models_dict()
    request.unhandled_logged_exceptions_count = unhandled_logged_exceptions_count
    request.unhandled_django_log_entry_count = unhandled_django_log_entry_count
    request.unhandled_javascript_error_count = unhandled_javascript_error_count

    return {
        "editable_models": editable_models,
        "unhandled_logged_exceptions_count": unhandled_logged_exceptions_count,
        "unhandled_django_log_entry_count": unhandled_django_log_entry_count,
        "settings": settings,
        "bootleg_settings": bootleg_settings,
    }
