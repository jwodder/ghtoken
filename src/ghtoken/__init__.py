"""
Look up GitHub access token in various sources

Visit <https://github.com/jwodder/ghtoken> for more information.
"""

from __future__ import annotations
import os
import subprocess
from dotenv import dotenv_values, find_dotenv

__version__ = "0.1.0.dev1"
__author__ = "John Thorvald Wodder II"
__author_email__ = "ghtoken@varonathe.org"
__license__ = "MIT"
__url__ = "https://github.com/jwodder/ghtoken"

__all__ = [
    "GitHubTokenNotFound",
    "get_github_token",
    "get_github_token_for_hub",
    "get_github_token_from_dotenv",
    "get_github_token_from_environ",
    "get_github_token_from_gh",
]

ENVVARS = ["GH_TOKEN", "GITHUB_TOKEN"]


class GitHubTokenNotFound(Exception):
    def __str__(self) -> str:
        return "GitHub access token not found"


def get_github_token(
    *,
    dotenv: bool | str | os.PathLike[str] = True,
    environ: bool = True,
    gh: bool = True,
    hub: bool = True,
) -> str:
    if dotenv is not False:
        if dotenv is True:
            path = None
        else:
            path = dotenv
        try:
            return get_github_token_from_dotenv(path)
        except GitHubTokenNotFound:
            pass
    if environ:
        try:
            return get_github_token_from_environ()
        except GitHubTokenNotFound:
            pass
    if gh:
        try:
            return get_github_token_from_gh()
        except GitHubTokenNotFound:
            pass
    if hub:
        try:
            return get_github_token_for_hub()
        except GitHubTokenNotFound:
            pass
    raise GitHubTokenNotFound()


def get_github_token_from_dotenv(path: str | os.PathLike[str] | None = None) -> str:
    if path is None:
        path = find_dotenv(usecwd=True)
    de_vars = dotenv_values(path)
    for varname in ENVVARS:
        value = de_vars.get(varname)
        if value is not None and value != "":
            return value
    raise GitHubTokenNotFound()


def get_github_token_from_environ() -> str:
    for varname in ENVVARS:
        value = os.environ.get(varname)
        if value is not None and value != "":
            return value
    raise GitHubTokenNotFound()


def get_github_token_from_gh() -> str:
    try:
        r = subprocess.run(
            ["gh", "auth", "token", "--hostname", "github.com"],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            check=True,
        )
    except (subprocess.CalledProcessError, OSError):
        raise GitHubTokenNotFound()
    else:
        token = r.stdout.strip()
        if token:
            return token
        else:
            raise GitHubTokenNotFound()


def get_github_token_for_hub() -> str:
    try:
        r = subprocess.run(
            ["git", "config", "--get", "hub.oauthtoken"],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            check=True,
        )
    except (subprocess.CalledProcessError, OSError):
        raise GitHubTokenNotFound()
    else:
        token = r.stdout.strip()
        if token:
            return token
        else:
            raise GitHubTokenNotFound()
