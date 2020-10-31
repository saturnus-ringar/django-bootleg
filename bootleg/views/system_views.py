from django.utils.translation import ugettext as _

from bootleg.system.git import GitData
from bootleg.views.base import StaffRequiredTemplateView


class DeployInfoView(StaffRequiredTemplateView):
    title = _("Deploy info")
    template_name = "bootleg/includes/deploy_info.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["git_data"] = GitData()
        return context
