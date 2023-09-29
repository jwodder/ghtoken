"""
Look up GitHub access token in various sources

Visit <https://github.com/jwodder/ghtoken> for more information.
"""

from __future__ import annotations
import os
from pathlib import Path
from dotenv import dotenv_values, find_dotenv

__version__ = "0.1.0.dev1"
__author__ = "John Thorvald Wodder II"
__author_email__ = "ghtoken@varonathe.org"
__license__ = "MIT"
__url__ = "https://github.com/jwodder/ghtoken"

ENVVARS = ["GH_TOKEN", "GITHUB_TOKEN"]


class GitHubTokenNotFound(Exception):
    def __str__(self) -> str:
        return "GitHub access token not found"


def get_github_token_from_dotenv(path: Path | str | None = None) -> str:
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
