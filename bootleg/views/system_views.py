from django.utils.functional import cached_property
from django.utils.translation import ugettext as _

from bootleg.system.system import System

from bootleg.system.git import GitData
from bootleg.utils.models import get_search_models, get_editable_models
from bootleg.views.base import SuperuserRequiredTemplateView
from bootleg.conf import bootleg_settings


class DeployInfoView(SuperuserRequiredTemplateView):
    page_title = _("Deployment")
    template_name = bootleg_settings.DEPLOYMENT_TEMPLATE

    @cached_property
    def git_data(self):
        return GitData()


class SystemInfoView(SuperuserRequiredTemplateView):
    page_title = _("System")
    template_name = bootleg_settings.SYSTEM_TEMPLATE

    @cached_property
    def system(self):
        return System()


class ModelsInfoView(SuperuserRequiredTemplateView):
    page_title = _("Models")
    template_name = "bootleg/system/models_info.html"

    def search_models(self):
        return get_search_models()

    def editable_models(self):
        return get_editable_models()


class DebugView(SuperuserRequiredTemplateView):
    page_title = _("Debug")
    template_name = "bootleg/system/debug.html"
