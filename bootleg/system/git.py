import git
import giturlparse
from django.conf import settings


class GitData:

    def __init__(self):
        self.repo = get_git_repo()
        self.github_url = get_github_url(self.repo)
        self.parsed_git_url = giturlparse.parse(self.repo.remotes.origin.url)


def get_github_url(repo):
    return giturlparse.parse(repo.remotes.origin.url).urls["https"].replace(".git", "")


def get_git_repo():
    return git.Repo(getattr(settings, "BASE_DIR"))


def git_pull():
    g = git.cmd.Git(getattr(settings, "BASE_DIR"))
    return g.pull()
