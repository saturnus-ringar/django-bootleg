import git
import giturlparse
from django.conf import settings


def get_github_url(repo):
    return giturlparse.parse(repo.remotes.origin.url).urls["https"].replace(".git", "")


def get_git_repo():
    return git.Repo(getattr(settings, "BASE_DIR"))


def git_pull():
    g = git.cmd.Git(getattr(settings, "BASE_DIR"))
    return g.pull()
