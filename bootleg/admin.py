from django.contrib import admin
from django.contrib import messages
from django.contrib.admin import ModelAdmin
from django.utils.translation import ugettext as _

from bootleg.db.models.django_log_entry import DjangoLogEntry
from bootleg.db.models.javascript_error import JavascriptError
from bootleg.db.models.javascript_error_message import JavascriptErrorMessage
from bootleg.db.models.logged_exception import LoggedException
from bootleg.db.models.profile import Profile
from bootleg.utils import strings


class BaseAdmin(admin.ModelAdmin):

    @property
    def media(self):
        media = super().media
        css = {
            "all": (
                "django_admin/css/model-admin.css",
            )
        }
        media._css_lists.append(css)
        return media


class ReadOnlyModelAdmin(BaseAdmin):

    def get_readonly_fields(self, request, obj=None):
        fields = []
        if not self.fields:
            for field in self.model._meta.fields:
                fields.append(field.name)
            for field in self.model._meta.many_to_many:
                fields.append(field.name)
            return fields

        return self.fields

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        if request.method not in ('GET', 'HEAD'):
            return False
        else:
            return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        return False

    def save_model(self, request, obj, form, change):
        pass

    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        return super().changeform_view(request, object_id, form_url, {
            'title': _(u'View {}'.format(self.model._meta.verbose_name))
        })


class TimeStampedModelAdmin(ModelAdmin):
    list_display = ["created", "modified"]
    date_hierarchy = "created"
    list_filter = ["created", "modified"]


class NameAndDescriptionAdmin(BaseAdmin):
    list_display = ["name", "description"]
    search_fields = ["name", "description"]


class TimeStampedNamedAndDescriptionAdmin(BaseAdmin):
    list_display = TimeStampedModelAdmin.list_display + NameAndDescriptionAdmin.list_display

    @property
    def media(self):
        media = super().media
        media._js_lists.append(["django_admin/js/time-stamped-named-and-description-admin.js"])
        return media


def handle_exceptions(modeladmin, request, queryset):
    for exception in queryset:
        exception.handle(request)
    messages.add_message(request, messages.INFO, _("The selected exceptions have been handled"))


handle_exceptions.short_description = _("Handle the exceptions")


@admin.register(Profile)
class ProfileAdmin(TimeStampedModelAdmin):
    list_display = TimeStampedModelAdmin.list_display + ["user"]
    search_fields = ["user__username"]


class ExceptionModelAdmin(TimeStampedModelAdmin, ReadOnlyModelAdmin):
    list_display = ["created", "clazz", "args", "formatted_stack_trace"]
    search_fields = ["clazz__name", "args", "stack_trace"]
    list_filter = ["clazz", "handled"]
    actions = [handle_exceptions]

    def formatted_stack_trace(self, obj):
        if obj.stack_trace:
            return strings.nl2br(obj.stack_trace)
        return None

    formatted_stack_trace.short_description = _("Stack trace")


@admin.register(DjangoLogEntry)
class DjangoLogEntryAdmin(ExceptionModelAdmin):
    list_display = ExceptionModelAdmin.list_display + ["log_level", "filename"]
    search_fields = ExceptionModelAdmin.search_fields + ["filename", "log_level__name"]
    list_filter = ExceptionModelAdmin.list_filter + ["log_level"]


@admin.register(LoggedException)
class DjangoLogEntryAdmin(ExceptionModelAdmin):
    pass


@admin.register(JavascriptError)
class JavascriptErrorAdmin(TimeStampedModelAdmin, ReadOnlyModelAdmin):
    list_display = ("created", "ip", "url", "line", "message")
    search_fields = ["ip", "url", "line", "message__message"]
    list_filter = ("message",)


@admin.register(JavascriptErrorMessage)
class JavascriptErrorMessageAdmin(ReadOnlyModelAdmin):
    list_display = ("message",)
