from __future__ import annotations
from dotenv import find_dotenv, dotenv_values
from pathlib import Path
import os

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
