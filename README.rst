.. image:: http://www.repostatus.org/badges/latest/wip.svg
    :target: http://www.repostatus.org/#wip
    :alt: Project Status: WIP — Initial development is in progress, but there
          has not yet been a stable, usable release suitable for the public.

.. image:: https://github.com/jwodder/ghtoken/workflows/Test/badge.svg?branch=master
    :target: https://github.com/jwodder/ghtoken/actions?workflow=Test
    :alt: CI Status

.. image:: https://codecov.io/gh/jwodder/ghtoken/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/jwodder/ghtoken

.. image:: https://img.shields.io/github/license/jwodder/ghtoken.svg
    :target: https://opensource.org/licenses/MIT
    :alt: MIT License

`GitHub <https://github.com/jwodder/ghtoken>`_
| `Issues <https://github.com/jwodder/ghtoken/issues>`_

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


Installation
============
``ghtoken`` requires Python 3.7 or higher.  Just use `pip
<https://pip.pypa.io>`_ for Python 3 (You have pip, right?) to install it::

    python3 -m pip install git+https://github.com/jwodder/ghtoken


API
===

.. code:: python

    ghtoken.get_github_token(
        *,
        dotenv: bool | str | os.PathLike[str] = True,
        environ: bool = True,
        gh: bool = True,
        hub: bool = True,
        git_hub: bool = True,
    ) -> str

Look up a GitHub access token by checking various sources (listed below) and
returning the first token found.  Individual sources can be disabled by setting
the corresponding keyword argument to ``False``.

The sources are as follows, listed in the order in which they are consulted:

``dotenv``
    Look for a ``.env`` file by searching from the current directory upwards
    and reading the first file found.  Alternatively, a specific file may be
    read by setting the ``dotenv`` keyword argument to the path to the file.
    If the file (whether found by searching or explicitly specified) cannot be
    read or parsed, control proceeds to the next enabled source.

    If the file contains a ``GH_TOKEN=...`` or ``GITHUB_TOKEN=...`` assignment
    with a non-empty value, that value is returned; otherwise, control proceeds
    to the next enabled source.  If assignments for both keys are present,
    ``GH_TOKEN`` takes precedence over ``GITHUB_TOKEN``.

    Reading values from a ``.env`` file will not modify the process's
    environment variables.

``environ``
    If the environment variable ``GH_TOKEN`` or ``GITHUB_TOKEN`` is set to a
    nonempty string, that variable's value is returned; otherwise, control
    proceeds to the next enabled source.  If both environment variables are
    set, ``GH_TOKEN`` takes precedence over ``GITHUB_TOKEN``.

``gh``
    Retrieve a GitHub access token stored for the gh_ command by running ``gh
    auth token --hostname github.com``.  If the command fails or outputs an
    empty line, control proceeds to the next enabled source.

    Note that, if gh has stored its access token in a system keyring, the user
    may be prompted to unlock the keyring.

    Note that, if the ``GH_TOKEN`` or ``GITHUB_TOKEN`` environment variable is
    set to a nonempty string, gh will return the value of the envvar rather
    than returning whatever access token may already be stored, and this
    happens even if the ``environ`` argument to ``get_github_token()`` is
    ``False``.

``hub``
    Retrieve a GitHub access token from the hub_ configuration file.  If the
    configuration file does not exist or is malformed, or if the file does not
    contain a nonempty token for the ``github.com`` domain, control proceeds to
    the next enabled source.

``git_hub``
    Retrieve a GitHub access token from the Git config key ``hub.oauthtoken``,
    used by the git-hub_ program.  If the key is set to the empty string, or if
    the Git config key ``hub.baseurl`` is set to a value other than
    ``https://api.github.com``, control proceeds to the next enabled source.

    Git config values are retrieved by running ``git config --get ...``.  If
    such a command fails, control proceeds to the next enabled source.

    If the ``hub.oauthtoken`` value starts with ``!``, the rest of the value is
    executed as a shell command, and the command's standard output (with
    leading & trailing whitespace stripped) is returned.

    .. _git-hub: https://github.com/sociomantic-tsunami/git-hub

If no enabled source returns a token, then a ``ghtoken.GitHubTokenNotFound``
exception is raised.