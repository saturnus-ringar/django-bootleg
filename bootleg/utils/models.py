import django
from django.apps import apps
from django.conf import settings
from django.contrib import admin
from django.core.exceptions import FieldDoesNotExist
from django.db import ProgrammingError, OperationalError, models
from django.db.models import CharField, EmailField
from django.urls import reverse
from django.utils.functional import LazyObject
from django_elasticsearch_dsl.registries import registry
from djangoql.schema import DjangoQLSchema

from bootleg.conf import bootleg_settings
from bootleg.utils.utils import get_meta_class_value, meta_class_value_is_true


def register_admin_model(model, admin_class):
    admin.site.unregister(model)
    admin.site.register(model, admin_class)


def get_default_admin_class(model):
    from bootleg.admin import ReadOnlyModelAdmin
    properties = {}
    if hasattr(model._meta, "visible_fields"):
        print(model.get_django_admin_fields())
        properties = {
            "list_display": model.get_django_admin_fields(),
            "search_fields": model.get_search_field_names(),
            "list_filter": model.get_filter_field_names()
        }
    return type("AdminClass%s" % model._meta.model_name, (ReadOnlyModelAdmin, ), properties)


# https://stackoverflow.com/a/44206637/9390372
def lazy_bulk_fetch(max_obj, max_count, fetch_func, start=0):
    counter = start
    while counter < max_count:
        yield fetch_func()[counter:counter + max_obj]
        counter += max_obj


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
    model_dict["class"] = model
    if hasattr(model._meta, "create_url"):
        model_dict["create_url"] = model._meta.create_url
    else:
        model_dict["create_url"] = reverse("bootleg:create_model", args=[model._meta.model_name])

    return model_dict


def get_editable_models():
    models = []
    for model in django.apps.apps.get_models():
        if model._meta.app_label == "bootleg":
            continue
        if hasattr(model._meta, "visible_fields"):
            models.append(model)
    models.sort(key=lambda x: x.get_order())
    return models


def get_verbose_names(models):
    model_names = []
    for model in models:
        model_names.append(model._meta.verbose_name)
    model_names.sort()
    return model_names


def get_editable_models_verbose_names():
    return get_verbose_names(get_editable_models())


def get_search_models_verbose_names():
    return get_verbose_names(get_search_models())


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


def get_input_order_by(model):
    ordering = get_meta_class_value(model, "input_ordering")
    if ordering:
        return ordering

    return get_order_by(model)


def get_order_by(model):
    ordering = get_meta_class_value(model, "ordering")
    if ordering:
        return ordering
    return ["-id"]


def display_model_in_menu(model, request, create=False):
    # the model is a dict here since it's used in templates
    if meta_class_value_is_true(model["class"], "exclude_from_menu"):
        # this one is configured to be excluded from the menu
        return False

    if create and not model["class"].is_allowed_to_edit(request.user):
        # creation and the user is not allowed to edit
        return False

    if not create and not model["class"].is_allowed_to_view(request.user):
        # listing and the user is not allowed to view this
        return False

    return True
