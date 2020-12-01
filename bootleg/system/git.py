import os

import git
import giturlparse
from django.conf import settings
from bootleg.conf import bootleg_settings


class GitData:

    def __init__(self):
        self.repo = get_git_repo()
        self.github_url = get_github_url(self.repo)
        self.parsed_git_url = giturlparse.parse(self.repo.remotes.origin.url)


def get_github_url(repo):
    parsed = giturlparse.parse(repo.remotes.origin.url)
    split = parsed.urls["https"].split("@")
    if len(split) > 1:
        return "https://" + split[1].replace(".git", "")
    else:
        return split[0]


def get_git_repo():
    return git.Repo(getattr(settings, "BASE_DIR"))


def git_pull():
    if bootleg_settings.GIT_USERNAME:
        os.environ["GIT_USERNAME"] = bootleg_settings.GIT_USERNAME
    print(bootleg_settings.GIT_USERNAME)
    print(os.getenv("GIT_USERNAME"))
    g = git.cmd.Git(getattr(settings, "BASE_DIR"))
    return g.pull()
