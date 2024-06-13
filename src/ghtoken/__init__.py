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

- :file:`.env` files
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

__version__ = "0.1.2"
__author__ = "John Thorvald Wodder II"
__author_email__ = "ghtoken@varonathe.org"
__license__ = "MIT"
__url__ = "https://github.com/jwodder/ghtoken"

__all__ = [
    "GHTokenNotFound",
    "get_ghtoken",
    "ghtoken_from_dotenv",
    "ghtoken_from_environ",
    "ghtoken_from_gh",
    "ghtoken_from_hub",
    "ghtoken_from_hub_oauthtoken",
]

ENVVARS = ["GH_TOKEN", "GITHUB_TOKEN"]


class GHTokenNotFound(Exception):
    """
    Exception raised by ghtoken functions when they fail to retrieve a GitHub
    access token
    """

    def __str__(self) -> str:
        return "GitHub access token not found"


def get_ghtoken(
    *,
    dotenv: bool | str | os.PathLike[str] = True,
    environ: bool = True,
    gh: bool = True,
    hub: bool = True,
    hub_oauthtoken: bool = True,
) -> str:
    """
    Retrieve a locally-stored GitHub access token by checking various sources
    and returning the first token found.  Individual sources can be disabled by
    setting the corresponding keyword argument to ``False``.

    The sources are as follows, listed in the order in which they are
    consulted.  Each source is implemented by a dedicated function which can be
    called on its own or in combination with other source functions if you need
    to do something novel.

    ``dotenv``
        Retrieve a token from a :file:`.env` file; implemented by
        `ghtoken_from_dotenv()` (q.v.).  If the ``dotenv`` keyword argument is
        set to a non-boolean, the argument's value is passed to
        `ghtoken_from_dotenv()`.

    ``environ``
        Retrieve a token from environment variables; implemented by
        `ghtoken_from_environ()` (q.v.).

    ``gh``
        Retrieve a token from the :command:`gh` command; implemented by
        `ghtoken_from_gh()` (q.v.).

    ``hub``
        Retrieve a token from the :command:`hub` configuration file;
        implemented by `ghtoken_from_hub()` (q.v.).

    ``hub_oauthtoken``
        Retrieve a token from the ``hub.oauthtoken`` Git config key;
        implemented by `ghtoken_from_hub_oauthtoken()` (q.v.).

    If no enabled source returns a token, a `GHTokenNotFound` exception is
    raised.
    """

    if dotenv is not False:
        if dotenv is True:
            path = None
        else:
            path = dotenv
        try:
            return ghtoken_from_dotenv(path)
        except GHTokenNotFound:
            pass
    if environ:
        try:
            return ghtoken_from_environ()
        except GHTokenNotFound:
            pass
    if gh:
        try:
            return ghtoken_from_gh()
        except GHTokenNotFound:
            pass
    if hub:
        try:
            return ghtoken_from_hub()
        except GHTokenNotFound:
            pass
    if hub_oauthtoken:
        try:
            return ghtoken_from_hub_oauthtoken()
        except GHTokenNotFound:
            pass
    raise GHTokenNotFound()


def ghtoken_from_dotenv(path: str | os.PathLike[str] | None = None) -> str:
    """
    Retrieve a GitHub access token from a :file:`.env` file

    Look for a :file:`.env` file by searching from the current directory
    upwards and reading the first file found.  Alternatively, a specific file
    may be read by supplying the path to the file.  If the file (whether found
    by searching or explicitly specified) cannot be read or parsed, a
    `GHTokenNotFound` exception is raised.

    If the file contains a ``GH_TOKEN=...`` or ``GITHUB_TOKEN=...`` assignment
    with a non-empty value, that value is returned; otherwise, a
    `GHTokenNotFound` exception is raised.  If assignments for both keys are
    present, ``GH_TOKEN`` takes precedence over ``GITHUB_TOKEN``.

    Reading values from a :file:`.env` file will not modify the process's
    environment variables.
    """
    if path is None:
        path = find_dotenv(usecwd=True)
    de_vars = dotenv_values(path)
    for varname in ENVVARS:
        value = de_vars.get(varname)
        if value is not None and value != "":
            return value
    raise GHTokenNotFound()


def ghtoken_from_environ() -> str:
    """
    Retrieve a GitHub access token from environment variables

    If the environment variable :envvar:`GH_TOKEN` or :envvar:`GITHUB_TOKEN` is
    set to a nonempty string, that variable's value is returned; otherwise, a
    `GHTokenNotFound` exception is raised.  If both environment variables are
    set, :envvar:`GH_TOKEN` takes precedence over :envvar:`GITHUB_TOKEN`.
    """
    for varname in ENVVARS:
        value = os.environ.get(varname)
        if value is not None and value != "":
            return value
    raise GHTokenNotFound()


def ghtoken_from_gh() -> str:
    """
    Retrieve a GitHub access token from the :command:`gh` command [docs__]

    __ https://github.com/cli/cli

    The token is retrieved by running ``gh auth token --hostname github.com``.
    If the command fails or outputs an empty line, a `GHTokenNotFound`
    exception is raised.

    Note that, if :command:`gh` has stored its access token in a system
    keyring, the user may be prompted to unlock the keyring.

    Note that, if the :environ:`GH_TOKEN` or :environ:`GITHUB_TOKEN`
    environment variable is set to a nonempty string, :command:`gh` will return
    the value of the envvar rather than returning whatever access token may
    already be stored.
    """
    try:
        r = subprocess.run(
            ["gh", "auth", "token", "--hostname", "github.com"],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            check=True,
        )
    except (subprocess.CalledProcessError, OSError):
        raise GHTokenNotFound()
    else:
        token = chomp(r.stdout)
        if token:
            return token
        else:
            raise GHTokenNotFound()


def ghtoken_from_hub() -> str:
    """
    Retrieve a GitHub access token from the configuration file for the
    :command:`hub` command [docs__]

    __ https://github.com/mislav/hub

    The location of the configuration file is determined as follows:

    - If the envvar :envvar:`HUB_CONFIG` is set to a nonempty string, the value
      of the envvar is used as the path to the file.

    - If the envvar :envvar:`XDG_CONFIG_HOME` is set to a nonempty string and
      :file:`$XDG_CONFIG_HOME/hub` exists, this path is used as the path to the
      file.

    - If :envvar:`XDG_CONFIG_HOME` is not set to a nonempty string and
      :file:`~/.config/hub` exists, this path is used as the path to the file.

    - The envvar :envvar:`XDG_CONFIG_DIRS` (defaulting to :file:`/etc/xdg` if
      the envvar is not set to a nonempty string) is split on the colon
      character to obtain a list of directories :file:`$dir`; the first
      :file:`$dir/hub` that exists is used as the path to the file.

    - If none of the above candidate paths exist, a `GHTokenNotFound` exception
      is raised.

    The configuration file must contain a YAML mapping that maps domain names
    to lists of sub-mappings that each contain an ``oauth_token`` key with a
    string value.  The ``oauth_token`` for the first element of the
    ``github.com`` domain is returned; if the file is malformed, the specified
    value does not exist, or the value equals an empty string, a
    `GHTokenNotFound` exception is raised.
    """
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
            raise GHTokenNotFound()
    else:
        path = Path(pathstr)
    try:
        with path.open(encoding="utf-8") as fp:
            cfg = YAML(typ="safe").load(fp)
    except Exception:
        raise GHTokenNotFound()
    try:
        token = cfg["github.com"][0]["oauth_token"]
    except (TypeError, AttributeError, LookupError):
        raise GHTokenNotFound()
    if isinstance(token, str) and token != "":
        return token
    else:
        raise GHTokenNotFound()


def ghtoken_from_hub_oauthtoken() -> str:
    """
    Retrieve a GitHub access token from the Git config key ``hub.oauthtoken``,
    used by the git-hub_ program.  If no value is set, or if the configured
    value is the empty string, a `GHTokenNotFound` exception is raised.

    If the Git config key ``hub.baseurl`` is set to a value other than
    ``https://api.github.com``, the retrieved token is assumed to be associated
    to an instance other than github.com, and so a `GHTokenNotFound` exception
    is raised.

    Git config values are retrieved by running ``git config --get ...``.  If
    such a command fails, a `GHTokenNotFound` exception is raised.

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
        raise GHTokenNotFound()
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
                raise GHTokenNotFound()
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
        raise GHTokenNotFound()


def chomp(s: str) -> str:
    """Remove a trailing LF, CR LF, or CR from ``s``, if any"""
    if s.endswith("\n"):
        s = s[:-1]
    if s.endswith("\r"):
        s = s[:-1]
    return s
