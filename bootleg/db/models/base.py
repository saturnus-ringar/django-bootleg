import datetime
from abc import abstractmethod

from annoying.functions import get_object_or_None
from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError, FieldDoesNotExist
from django.db import models
from django.db.models import CharField, EmailField
from django.db.models.fields.files import ImageField
from django.db.models.manager import Manager
from django.urls import reverse
from django.utils import formats
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _
from django_elasticsearch_dsl import TextField, ObjectField
from django_elasticsearch_dsl.registries import registry
from django_elasticsearch_dsl.search import Search
from django_extensions.db.models import TimeStampedModel
from djangoql.queryset import DjangoQLQuerySet

from bootleg.logging import logging
from bootleg.utils import strings
from bootleg.utils.lists import add_unique
from bootleg.utils.models import get_foreign_key_field
from bootleg.utils.utils import get_meta_class_value


##########################################
# managers
##########################################

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

    dql_objects = DjangoQLQuerySet.as_manager()
    # adding a default manager here - if I don't I get "type object '<Class>' has no attribute 'objects'"
    # when I added the dql_objects-manager
    objects = Manager()

    ##############################
    # basic thingies
    ##############################

    def get_model_name(self):
        return self._meta.model_name

    ##############################
    # fields
    ##############################

    @classmethod
    def is_valid_foreign_field(cls, field_name):
        if get_foreign_key_field(cls, field_name):
            return True

        return False

    @classmethod
    def is_valid_search_field(cls, field_name):
        if field_name in cls.get_search_field_names():
            return True

        if cls.is_valid_foreign_search_field(field_name):
            return True

        return False

    @classmethod
    def is_valid_foreign_search_field(cls, field_name):
        try:
            field = cls._meta.get_field(field_name)
            if hasattr(field, "related_model"):
                return True
        except FieldDoesNotExist:
            pass

        return cls.is_valid_foreign_field(field_name)

    @classmethod
    def get_meta_value(cls, attr):
        return get_meta_class_value(cls, attr)

    @classmethod
    def get_visible_fields(cls):
        fields = cls.get_meta_list("visible_fields")
        if fields == "__all__":
            fields = cls.get_all_field_names()
            fields.remove("id")
            if "modified" in fields:
                # a special case for modified auto_now-fields... hmmm
                field = cls._meta.get_field("modified")
                if field.auto_now:
                    fields.remove("modified")
            return fields
        return fields

    @classmethod
    def get_meta_list(cls, attr):
        list = get_meta_class_value(cls, attr)
        if list:
            return list

        return []

    @classmethod
    def has_field(cls, field_name):
        if field_name in cls.get_all_field_names():
            return True

        return False

    @classmethod
    def get_prefetch_related(cls):
        return cls.get_meta_value("prefetch_related")

    @classmethod
    def get_all_field_names(cls):
        field_names = []
        for field in cls._meta.fields:
            field_names.append(field.name)
        for many_to_many in cls.get_many_to_many_fields(cls):
            field_names.append(many_to_many.name)
        return field_names

    @classmethod
    def get_search_field_names(cls):
        classes = [CharField, EmailField]
        fields = []
        for field in cls._meta.fields:
            if field.__class__ in classes:
                fields.append(field.name)

        if hasattr(cls._meta, "extra_search_fields"):
            fields += cls._meta.extra_search_fields

        return fields

    @classmethod
    def get_autocomplete_fields(cls):
        fields = []
        autocomplete_fields = get_meta_class_value(cls, "autocomplete_fields")
        if autocomplete_fields:
              fields += autocomplete_fields

        # add (uniqe) search document fields, if any
        fields = add_unique(fields, cls.get_search_document_field_names())
        if fields:
            return fields

        return cls.get_search_field_names()

    @classmethod
    def get_foreign_key_fields(cls):
        fields = []
        for field in cls._meta.fields:
            if field.get_internal_type() == "ForeignKey":
                fields.append(field)

        return fields

    @classmethod
    def get_foreign_key_field_names(cls):
        field_names = []
        for field in cls.get_foreign_key_fields():
            field_names.append(field.name)

        return field_names

    @classmethod
    def get_filter_field_names(cls):
        fields = cls.get_meta_list("filter_fields")
        if fields == "__all__":
            return cls.get_all_field_names()

        return fields

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

    def get_fields(self):
        return self._meta.fields

    def get_many_to_many_fields(self):
        return self._meta.many_to_many

    def get_many_to_one_objects(self):
        objects = dict()
        for related_object in self._meta.related_objects:
            verbose_name_plural = related_object.remote_field.model._meta.verbose_name_plural
            if verbose_name_plural not in objects:
                objects[verbose_name_plural] = dict()
                objects[verbose_name_plural]["objects"] = []
            accessor = related_object.get_accessor_name()
            for object in getattr(self, accessor).all():
                objects[verbose_name_plural]["objects"].append(object)
        return objects

    def get_many_to_one_accessors(self):
        accessors = []
        for field in self._meta.related_objects:
            accessors.append(field.get_accessor_name())

        return accessors

    ##############################
    # elastic search
    ##############################
    @classmethod
    def get_search_document_field_names(cls):
        field_names = []
        document = cls.get_search_document()
        if document:
            for field_name, field in document._doc_type.mapping.properties.properties.to_dict().items():
                if isinstance(field, TextField):
                    field_names.append(field_name)
                elif isinstance(field, ObjectField):
                    # this was the first way I found how to get the properties :|
                    for property in field.to_dict()["properties"]:
                        remote_field_name = field_name + "__" + property
                        if get_foreign_key_field(cls, remote_field_name):
                            field_names.append(remote_field_name)

        return field_names

    @classmethod
    def get_search_document(cls):
        for doc in registry.get_documents():
            # works, I guess, I had some trouble with type() comparisons
            if str(doc.Django.model) == str(cls):
                return doc

        return None

    @classmethod
    def get_search_index_total_count_results(cls):
        doc = cls.get_search_document()
        if doc:
            return Search(index=doc._index._name)

        return None

    @classmethod
    def get_search_index_total_count(cls):
        sr = cls.get_search_index_total_count_results()
        if sr:
            return sr.count()

        return None

    @classmethod
    def get_count(cls):
        return cls.objects.all().count()

    ##############################
    # urls
    ##############################
    @classmethod
    def get_changelist_url(cls):
        return reverse('admin:%s_%s_changelist' % (cls._meta.app_label, cls._meta.model_name))

    @classmethod
    def get_list_url(cls):
        return reverse("bootleg:list_view", args=[cls._meta.model_name])

    @classmethod
    def get_autocomplete_url(self):
        if self.get_search_field_names():
            return reverse("bootleg:json_autocomplete", args=[self._meta.model_name])

        return None

    def get_admin_url(self):
        return reverse('admin:%s_%s_change' % (self._meta.app_label,  self._meta.model_name),  args=[self.id])

    def get_admin_add_url(self):
        return reverse('admin:%s_%s_add' % (self._meta.app_label,  self._meta.model_name))

    def get_add_url(self):
        return reverse("bootleg:create_model", args=[self._meta.model_name])

    def get_update_url(self):
        return reverse("bootleg:update_model", args=[self._meta.model_name, self.id])

    def get_delete_url(self):
        return reverse("bootleg:delete_model", args=[self._meta.model_name, self.id])

    def get_detail_url(self):
        return reverse("bootleg:model_detail", args=[self._meta.model_name, self.id])

    def get_clone_url(self):
        return reverse("bootleg:clone_model", args=[self._meta.model_name, self.id])

    ##############################
    # miscish.... for templates
    ##############################

    @classmethod
    def get_verbose_name(cls):
        return cls._meta.verbose_name

    ##############################
    # links
    ##############################

    def get_admin_link(self, target_blank=True):
        if not target_blank:
            return mark_safe("<a href='%s'>%s</a>" % (self.get_admin_url(), self.get_admin_url()))
        else:
            return mark_safe("<a href='%s' target='_blank'>%s</a>" % (self.get_admin_url(), self.get_admin_url()))

    def get_button_link(self, url, text):
        return mark_safe('<a href="%s"><button class ="btn btn-primary btn-sm">%s</button></a>'
                         % (url, text))

    def get_detail_link(self):
        return self.get_button_link(self.get_detail_url(), _("View"))

    def get_ajax_detail_link(self):
        return mark_safe('<a href="" class="object-view-loader" data-url="%s" data-object-id="%s" '
                         'data-hide-text="%s"><button data-object-id="%s" class="btn btn-primary btn-sm">'
                         '%s</button></a>'
                 % (reverse("bootleg:model_detail", args=[self._meta.model_name, self.id]),
                    self.id,
                    _("Hide"),
                    self.id,
                    _("View")))

    def get_update_link(self):
        return self.get_button_link(self.get_update_url(), _("Update"))

    def get_delete_link(self):
        return mark_safe('<a href="%s" class="confirmation-link" data-text="%s">'
                         '<button class ="btn btn-danger btn-sm">%s</button></a>'
                         % (self.get_delete_url(), _("Are you sure you want to delete this?"), _("Delete")))

    def get_clone_link(self):
        return mark_safe('<a href="%s" class="confirmation-link" data-text="%s">'
                         '<button class ="btn btn-warning btn-sm">%s</button></a>'
                         % (self.get_clone_url(), _("Are you sure you want to clone this?"), _("Clone")))

    def get_absolute_url_link(self):
        if hasattr(self, "get_absolute_url"):
            return mark_safe('<a href="%s">%s</a>' % (self.get_absolute_url(), self.get_absolute_url()))

    @abstractmethod
    def to_log(self):
        raise NotImplementedError

    class Meta:
        abstract = True


class NameModel(BaseModel):
    name = models.CharField(max_length=255, db_index=True, unique=True, null=False, blank=False, verbose_name=_("Name"))

    def fix_clone_data(self):
        self.name = _("Cloned %s - %s" % (self._meta.verbose_name,
                                          formats.date_format(datetime.datetime.now(), settings.DATETIME_FORMAT)))

    def __str__(self):
        return self.name

    class Meta:
        abstract = True
        ordering = ["name"]


class NameAndDescriptionModel(NameModel):
    description = models.TextField(null=False, blank=False, verbose_name=_("Description"))

    def to_log(self):
        return "Name: [%s] Description: [%s]" % (self.name, strings.truncate(self.description))

    def __str__(self):
        return self.name

    class Meta:
        abstract = True
        visible_fields = ["name", "description"]


class EditableNameAndDescriptionModel(NameAndDescriptionModel, TimeStampedModel):

    def __str__(self):
        return self.name

    class Meta(NameAndDescriptionModel.Meta):
        abstract = True
        #admin_class = TimeStampedNamedAndDescriptionAdmin
        #admin_class = "SHISH"


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


# monkey patch django's user clean
def clean_user(self):
    if self.email:
        if get_object_or_None(User, email=self.email):
            raise ValidationError("A user with this email adress already exists.")


User.clean = clean_user

