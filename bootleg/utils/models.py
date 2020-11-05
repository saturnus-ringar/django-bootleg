import django
from django.apps import apps
from django.db import ProgrammingError, OperationalError
from django.db.models import Q
from django.urls import reverse
from django.conf import settings


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


def search(model, fields, query):
    qr = None
    for field in fields:
        q = Q(**{"%s__icontains" % field: query})
        if qr:
            qr = qr | q
        else:
            qr = q

        return model.objects.filter(qr).order_by("id")
