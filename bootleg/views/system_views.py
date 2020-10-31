import giturlparse
from bootleg.git import git

from bootleg.views.base import StaffRequiredTemplateView
from django.utils.translation import ugettext as _


class DeployStatusView(StaffRequiredTemplateView):
    title = _("Deploy status")
    template_name = "mantis/deploy_status.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        repo = git.get_git_repo()
        context["repo"] = repo
        context["github_url"] = git.get_github_url(repo)
        context["parsed_url"] = giturlparse.parse(repo.remotes.origin.url)
        return context
