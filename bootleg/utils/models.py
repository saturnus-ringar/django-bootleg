import django
from django.apps import apps
from django.conf import settings
from django.core.exceptions import FieldDoesNotExist
from django.db import ProgrammingError, OperationalError
from django.db.models import Q, CharField
from django.urls import reverse

from bootleg.conf import bootleg_settings
from bootleg.utils.utils import get_meta_class_value


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
    models.sort(key=lambda x: x._meta.model_name, reverse=True)
    return models


def get_editable_model_verbose_names():
    model_names = []
    for model in get_editable_models():
        model_names.append(model._meta.verbose_name)
    model_names.sort()
    return model_names


def filter_autocomplete_fields(model, fields):
    included_types = [CharField]
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
        foreign_key_model = model._meta.get_field(parts[0]).related_model
        if foreign_key_model:
            return foreign_key_model._meta.get_field(parts[1])
        else:
            return None
    except FieldDoesNotExist:
        return None


def get_order_by(model):
    ordering = get_meta_class_value(model, "ordering")
    if ordering:
        return ordering
    return ["-id"]


def search_and_filter(model, query=None, args=None, autocomplete=False):
    queryset = None
    if query:
        queryset = search(model, model.get_search_field_names(), query, autocomplete=autocomplete)

    if queryset is None:
        queryset = model.objects.all()

    if args:
        # got args... filter
        queryset = queryset.filter(**args)

    queryset = queryset.order_by(*get_order_by(model))
    return queryset.select_related(*model.get_foreign_key_field_names())


# https://stackoverflow.com/a/1239602/9390372
def search(model, fields, query, autocomplete=False):
    if autocomplete:
        fields = filter_autocomplete_fields(model, fields)
    qr = None
    for field in fields:
        dx(field)
        if not autocomplete:
            q = Q(**{"%s__icontains" % field: query})
        else:
            q = Q(**{"%s__istartswith" % field: query})

        if qr:
            qr = qr | q
        else:
            qr = q

    return model.objects.filter(qr).distinct().order_by("id")
