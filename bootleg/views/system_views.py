from bootleg.system.system import System
from django.utils.translation import ugettext as _

from bootleg.system.git import GitData
from bootleg.views.base import StaffRequiredTemplateView
from bootleg.conf.settings import bootleg_settings


class DeployInfoView(StaffRequiredTemplateView):
    title = _("Deployment")
    template_name = bootleg_settings.SYSTEM_TEMPLATE

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["git_data"] = GitData()
        return context


class SystemInfoView(StaffRequiredTemplateView):
    title = _("System")
    template_name = bootleg_settings.SYSTEM_TEMPLATE

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["system"] = System()
        return context
