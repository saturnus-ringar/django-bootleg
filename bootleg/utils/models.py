import django
from django.apps import apps
from django.conf import settings
from django.core.exceptions import FieldDoesNotExist
from django.db import ProgrammingError, OperationalError, models
from django.db.models import Q, CharField, EmailField
from django.urls import reverse
from django.utils.functional import LazyObject
from djangoql.exceptions import DjangoQLError
from djangoql.queryset import apply_search
from djangoql.schema import DjangoQLSchema

from bootleg.conf import bootleg_settings
from bootleg.utils.utils import get_meta_class_value
from django_elasticsearch_dsl.registries import registry


# https://stackoverflow.com/a/48264821/9390372
class SearchResults(LazyObject):

    def __init__(self, search_object):
        self._wrapped = search_object

    def __len__(self):
        return self._wrapped.count()

    def __getitem__(self, index):
        search_results = self._wrapped[index]
        if isinstance(index, slice):
            search_results = list(search_results)
        return search_results


def get_text_type_fields():
    return (models.CharField,
        models.DateField,
        models.EmailField,
        models.GenericIPAddressField,
        models.TextField,
        models.TimeField,
        models.URLField)


class GenericDjangoQLSchema(DjangoQLSchema):

    def get_fields(self, model):
        fields = []
        for field in model._meta.fields:
            if "password" in field.name:
                continue
            if field.__class__ in get_text_type_fields() or field.related_model:
                fields.append(field.name)

        return sorted(fields)


class ModelSearcher:

    def __init__(self, model, query=None, dql_query=None, args=None, autocomplete=False, es_limit=None):
        self.model = model
        self.es_limit = es_limit
        self.query = query
        self.dql_query = dql_query
        self.document = None
        self.args = args
        self.autocomplete = autocomplete
        self.queryset = self.model.objects.all()
        self.search_results = None

    def is_search(self):
        if self.query:
            return True
        elif self.dql_query:
            return True
        elif self.args:
            return True

        return False

    def search(self):
        self.dql_search()
        self.query_search()
        self.filter_by_args()
        self.queryset = self._get_queryset()

    def _get_queryset(self):
        prefetch_related = self.model.get_prefetch_related()
        if prefetch_related:
            self.queryset = self.queryset.prefetch_related(*prefetch_related)
        return self.queryset.order_by(*get_order_by(self.model))

    def dql_search(self):
        try:
            if self.dql_query:
                self.queryset = apply_search(self.model.objects.all(), self.dql_query)
        except DjangoQLError:
            pass

    # https://stackoverflow.com/a/1239602/9390372
    def query_search(self):
        if not self.query:
            # ugly return, indeed!
            return

        self.document = self.model.get_search_document()
        if self.document:
            return self.elastic_search()

        if self.autocomplete:
            fields = filter_autocomplete_fields(self.model, self.model.get_autocomplete_fields())
        else:
            fields = self.model.get_search_field_names()

        self.queryset = self.queryset.filter(self.get_qr(fields)).distinct().order_by("id")

    def get_qr(self, fields):
        qr = None
        for field in fields:
            if not self.autocomplete:
                q = Q(**{"%s__icontains" % field: self.query})
            else:
                q = Q(**{"%s__istartswith" % field: self.query})

            if qr:
                qr = qr | q
            else:
                qr = q

        return qr

    def elastic_search(self):
        if not self.es_limit:
            raise ValueError("Can't (elastic) search without a search limit (es_limit).")
        results = self.document.search().filter("multi_match", query=self.query,
                                                       fields=self.document.Django.fields)[:self.es_limit]
        self.search_results = SearchResults(results)
        self.queryset = results.to_queryset()

    def filter_by_args(self):
        if self.args:
            self.queryset = self.queryset.filter(**self.args)


def is_valid_profile_model():
    try:
        model = get_profile_model()
        for base in model.__bases__:
            if "bootleg.db.models.profile.Profile" in str(base):
                return True
    except:
        return False


def get_profile_model():
    if getattr(settings, "PROFILE_MODEL", None):
        return apps.get_model(settings.PROFILE_MODEL)


def setup_default_site():
    # getting AppRegistryNotReady("Apps aren't loaded yet.") without this local import :|
    from django.contrib.sites.models import Site
    save_site = False
    site = None
    try:
        site = Site.objects.get(id=settings.SITE_ID)
    except Site.DoesNotExist as e:
        save_site = True
    except (OperationalError, ProgrammingError) as e:
        # we'll get them OperationalError, ProgrammingErrors when the first migrate is run, and DoesNotExist ...
        return

    # the example.com site might exist
    if site and site.domain == "example.com":
        save_site = True

    if not site:
        site = Site()
        save_site = True

    if save_site:
        site.name = bootleg_settings.SITE_NAME
        site.domain = bootleg_settings.SITE_DOMAIN
        site.save()


def get_search_models():
    models = []
    for doc in registry.get_documents():
        models.append(doc.Django.model)

    return models


def get_editable_by_name(model_name):
    for model in get_editable_models():
        split = model._meta.model_name.split(".")
        if split[0] == model_name:
            return model

    return None


def get_editable_models_dict():
    models = []
    for model in get_editable_models():
        models.append(get_model_dict(model))
    return models


def get_model_dict(model):
    model_dict = dict()
    model_dict["meta"] = model._meta
    if hasattr(model._meta, "create_url"):
        model_dict["create_url"] = model._meta.create_url
    else:
        model_dict["create_url"] = reverse("bootleg:create_model", args=[model._meta.model_name])

    return model_dict


def get_editable_models():
    models = []
    for model in django.apps.apps.get_models():
        if hasattr(model._meta, "visible_fields"):
            models.append(model)
    models.sort(key=lambda x: x._meta.model_name)
    return models


def get_editable_model_verbose_names():
    model_names = []
    for model in get_editable_models():
        model_names.append(model._meta.verbose_name)
    model_names.sort()
    return model_names


def filter_autocomplete_fields(model, fields):
    included_types = [CharField, EmailField]
    filtered_fields = []
    for field_name in fields:
        try:
            if "__" in field_name:
                field = get_foreign_key_field(model, field_name)
            else:
                field = model._meta.get_field(field_name)
            if type(field) in included_types:
                filtered_fields.append(field_name)
        except FieldDoesNotExist:
            pass

    return filtered_fields


def get_foreign_key_field(model, field):
    # must be in model__field_name-format
    try:
        parts = field.split("__")
        if len(parts) > 1:
            foreign_key_model = model._meta.get_field(parts[0]).related_model
            if foreign_key_model:
                return foreign_key_model._meta.get_field(parts[1])
            else:
                return None
        else:
            return None
    except FieldDoesNotExist:
        return None


def get_order_by(model):
    ordering = get_meta_class_value(model, "ordering")
    if ordering:
        return ordering
    return ["-id"]

