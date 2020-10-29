from django.apps import AppConfig

from bootleg.utils import models


class BootlegConfig(AppConfig):
    name = 'bootleg'

    def ready(self):
        models.setup_default_site()
