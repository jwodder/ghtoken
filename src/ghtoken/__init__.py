"""
Retrieve GitHub access tokens from various sources

When writing a Python program for interacting with GitHub's API, you'll likely
want to use the local user's GitHub access token for authentication.  Asking
the user to provide the token every time is undesirable, so you'd rather look
up the token in some well-known storage location.  The problem is, there have
been so many places to store GitHub tokens supported by different programs over
the years, and asking your users to migrate to a new one shouldn't be
necessary.

That's where ``ghtoken`` comes in: it provides a single function for checking
multiple well-known sources for GitHub access tokens plus separate functions
for querying individual sources in case you need to combine the queries in
novel ways.

The following token sources are currently supported:

- ``.env`` files
- environment variables
- the gh_ command
- the hub_ configuration file
- the ``hub.oauthtoken`` Git config option

.. _gh: https://github.com/cli/cli
.. _hub: https://github.com/mislav/hub

Visit <https://github.com/jwodder/ghtoken> for more information.
"""

from __future__ import annotations
import os
from pathlib import Path
import subprocess
from dotenv import dotenv_values, find_dotenv
from ruamel.yaml import YAML

__version__ = "0.1.0.dev1"
__author__ = "John Thorvald Wodder II"
__author_email__ = "ghtoken@varonathe.org"
__license__ = "MIT"
__url__ = "https://github.com/jwodder/ghtoken"

__all__ = [
    "GitHubTokenNotFound",
    "get_github_token",
    "get_github_token_for_git_hub",
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
    git_hub: bool = True,
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
    if git_hub:
        try:
            return get_github_token_for_git_hub()
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
        token = chomp(r.stdout)
        if token:
            return token
        else:
            raise GitHubTokenNotFound()


def get_github_token_for_hub() -> str:
    pathstr = os.environ.get("HUB_CONFIG", "")
    if pathstr == "":
        config_dir = os.environ.get("XDG_CONFIG_HOME", "")
        if config_dir == "":
            config_dir = str(Path.home() / ".config")
        xdg_dirs = os.getenv("XDG_CONFIG_DIRS", "")
        if xdg_dirs == "":
            xdg_dirs = "/etc/xdg"
        for d in [config_dir, *xdg_dirs.split(":")]:
            path = Path(d, "hub")
            if path.exists():
                break
        else:
            raise GitHubTokenNotFound()
    else:
        path = Path(pathstr)
    try:
        with path.open() as fp:
            cfg = YAML(typ="safe").load(fp)
    except Exception:
        raise GitHubTokenNotFound()
    try:
        token = cfg["github.com"][0]["oauth_token"]
    except (TypeError, AttributeError, LookupError):
        raise GitHubTokenNotFound()
    if isinstance(token, str) and token != "":
        return token
    else:
        raise GitHubTokenNotFound()


def get_github_token_for_git_hub() -> str:
    """
    Retrieve a GitHub access token from the Git config key ``hub.oauthtoken``,
    used by the git-hub_ program.  If no value is set, or if the configured
    value is the empty string, `GitHubTokenNotFound` is raised.

    If the Git config key ``hub.baseurl`` is also set to a value other than
    ``https://api.github.com``, the retrieved token is assumed to be associated
    to an instance other than github.com, and so `GitHubTokenNotFound` is
    raised.

    If the retrieved value starts with ``!``, the rest of the value is executed
    as a shell command, and the command's standard output (with leading &
    trailing whitespace stripped) is returned.

    .. _git-hub: https://github.com/sociomantic-tsunami/git-hub
    """
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
        token = chomp(r.stdout)
        if token:
            try:
                r = subprocess.run(
                    [
                        "git",
                        "config",
                        "--get",
                        "--default",
                        "https://api.github.com",
                        "hub.baseurl",
                    ],
                    text=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.DEVNULL,
                    check=True,
                )
            except (subprocess.CalledProcessError, OSError):
                raise GitHubTokenNotFound()
            if chomp(r.stdout) == "https://api.github.com":
                if token.startswith("!"):
                    return subprocess.run(
                        token[1:],
                        shell=True,
                        text=True,
                        stdout=subprocess.PIPE,
                        check=True,
                    ).stdout.strip()
                else:
                    return token
        raise GitHubTokenNotFound()


def chomp(s: str) -> str:
    """Remove a trailing LF, CR LF, or CR from ``s``, if any"""
    if s.endswith("\n"):
        s = s[:-1]
    if s.endswith("\r"):
        s = s[:-1]
    return s
