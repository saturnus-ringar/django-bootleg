from abc import abstractmethod

from django.db import models
from django.db.models.fields.files import ImageField
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _
from django_extensions.db.models import TimeStampedModel

from bootleg.logging import logging
from bootleg.utils import strings


##########################################
# managers
##########################################


class NameAndDescriptionManager(models.Manager):

    def search_flat(self, query):
        return self.search(query).values_list("name", flat=True)

    def search(self, query):
        return self.model.objects.filter(name__icontains=query)


class UnhandledStatusModelManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().filter(handled=False)


class LoggedExceptionManager(models.Manager):

    def create(self, clazz, traceback, args):
        # circular-import-fix :|
        from bootleg.db.models.logged_exception import LoggedException
        from bootleg.db.models.klass import Class
        clazz, created = Class.objects.get_or_create(name=clazz)
        logged_exception = LoggedException()
        logged_exception.stack_trace = traceback
        logged_exception.clazz = clazz
        logged_exception.args = args
        logged_exception.save()


##########################################
# base models
##########################################

class BaseModel(models.Model):

    @classmethod
    def get_changelist_url(cls):
        return reverse('admin:%s_%s_changelist' % (cls._meta.app_label, cls._meta.model_name))

    @classmethod
    def get_autocomplete_url(self):
        if hasattr(self._meta, "autocomplete_field"):
            return reverse("bootleg:json_suggest", args=[self._meta.model_name])

        return None

    def get_simple_fields_except_id(self):
        excluded_field_types = [ImageField]
        fields = []
        for field in self._meta.fields:
            if field.name != "id" and not type(field) in excluded_field_types:
                fields.append(field)
        return fields

    def get_image_fields(self):
        fields = []
        for field in self._meta.fields:
            if isinstance(field, ImageField):
                fields.append(field)
        return fields

    def get_model_name(self):
        return self._meta.model_name

    def get_fields(self):
        return self._meta.fields

    def get_many_to_many_fields(self):
        return self._meta.many_to_many

    def get_admin_link(self, target_blank=True):
        if not target_blank:
            return mark_safe("<a href='%s'>%s</a>" % (self.get_admin_url(), self.get_admin_url()))
        else:
            return mark_safe("<a href='%s' target='_blank'>%s</a>" % (self.get_admin_url(), self.get_admin_url()))

    def get_admin_url(self):
        return reverse('admin:%s_%s_change' % (self._meta.app_label,  self._meta.model_name),  args=[self.id])

    def get_admin_add_url(self):
        return reverse('admin:%s_%s_add' % (self._meta.app_label,  self._meta.model_name))

    def get_add_url(self):
        return reverse("bootleg:create_model", args=[self._meta.model_name])

    def get_add_url(self):
        return reverse("bootleg:update_model", args=[self._meta.model_name, self.id])

    def get_update_link(self):
        return mark_safe('<a href="%s"><button class ="btn btn-primary btn-sm">%s</button></a>'
                         % (self.get_add_url(), _("Update")))

    @abstractmethod
    def to_log(self):
        raise NotImplementedError

    class Meta:
        abstract = True


class NameModel(BaseModel):
    name = models.CharField(max_length=255, unique=True, null=False, blank=False, verbose_name=_("Name"))

    def __str__(self):
        return self.name

    class Meta:
        abstract = True
        ordering = ["name"]


class NameAndDescriptionModel(NameModel):
    description = models.TextField(null=False, blank=False, verbose_name=_("Description"))

    objects = NameAndDescriptionManager()

    def to_log(self):
        return "Name: [%s] Description: [%s]" % (self.name, strings.truncate(self.description))

    def __str__(self):
        return self.name

    class Meta:
        abstract = True
        visible_fields = ["name", "description"]
        search_fields = ["name", "description"]
        autocomplete_field = "name"


class EditableNameAndDescriptionModel(NameAndDescriptionModel, TimeStampedModel):

    def __str__(self):
        return self.name

    class Meta(NameAndDescriptionModel.Meta):
        abstract = True
        #admin_class = TimeStampedNamedAndDescriptionAdmin
        admin_class = "SHISH"


class HandledStatusModel(BaseModel, TimeStampedModel):
    handled = models.BooleanField(default=False, null=False, blank=False)

    unhandled = UnhandledStatusModelManager()

    class Meta:
        abstract = True


class ExceptionModel(HandledStatusModel):
    stack_trace = models.TextField(null=True, blank=False)
    args = models.CharField(max_length=1024, null=False, blank=False)
    clazz = models.ForeignKey("bootleg.Class", on_delete=models.CASCADE)

    objects = LoggedExceptionManager()

    def handle(self, request):
        self.handled = True
        self.save()
        logging.log_audit(logging.HANDLED + " the exception with id: [%s]" % self.id, request)

    class Meta:
        abstract = True
