|repostatus| |ci-status| |coverage| |pyversions| |license|

.. |repostatus| image:: https://www.repostatus.org/badges/latest/active.svg
    :target: https://www.repostatus.org/#active
    :alt: Project Status: Active — The project has reached a stable, usable
          state and is being actively developed.

.. |ci-status| image:: https://github.com/jwodder/ghtoken/actions/workflows/test.yml/badge.svg
    :target: https://github.com/jwodder/ghtoken/actions/workflows/test.yml
    :alt: CI Status

.. |coverage| image:: https://codecov.io/gh/jwodder/ghtoken/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/jwodder/ghtoken

.. |pyversions| image:: https://img.shields.io/pypi/pyversions/ghtoken.svg
    :target: https://pypi.org/project/ghtoken/

.. |license| image:: https://img.shields.io/github/license/jwodder/ghtoken.svg
    :target: https://opensource.org/licenses/MIT
    :alt: MIT License

`GitHub <https://github.com/jwodder/ghtoken>`_
| `PyPI <https://pypi.org/project/ghtoken/>`_
| `Issues <https://github.com/jwodder/ghtoken/issues>`_
| `Changelog <https://github.com/jwodder/ghtoken/blob/master/CHANGELOG.md>`_

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
``ghtoken`` requires Python 3.8 or higher.  Just use `pip
<https://pip.pypa.io>`_ for Python 3 (You have pip, right?) to install it::

    python3 -m pip install ghtoken


API
===

Note: When retrieving GitHub access tokens, no validation of the token format
is performed other than rejecting empty strings.

.. code:: python

    ghtoken.get_ghtoken(
        *,
        dotenv: bool | str | os.PathLike[str] = True,
        environ: bool = True,
        gh: bool = True,
        hub: bool = True,
        hub_oauthtoken: bool = True,
    ) -> str

Retrieve a locally-stored GitHub access token by checking various sources
(listed below) and returning the first token found.  Individual sources can be
disabled by setting the corresponding keyword argument to ``False``.

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
    Retrieve a GitHub access token stored by the gh_ command by running ``gh
    auth token --hostname github.com``.  If the command fails or outputs an
    empty line, control proceeds to the next enabled source.

    Note that, if gh has stored its access token in a system keyring, the user
    may be prompted to unlock the keyring.

    Note that, if the ``GH_TOKEN`` or ``GITHUB_TOKEN`` environment variable is
    set to a nonempty string, gh will return the value of the envvar rather
    than returning whatever access token may already be stored, and this
    happens even if the ``environ`` argument to ``get_ghtoken()`` is ``False``.

``hub``
    Retrieve a GitHub access token from the hub_ configuration file.  If the
    configuration file does not exist or is malformed, or if the file does not
    contain a nonempty token for the ``github.com`` domain, control proceeds to
    the next enabled source.

``hub_oauthtoken``
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

If no enabled source returns a token, then a ``ghtoken.GHTokenNotFound``
exception is raised.

.. code:: python

    ghtoken.ghtoken_from_dotenv(path: str | os.PathLike[str] | None = None) -> str

Retrieve a GitHub access token from an ``.env`` file as described above.  A
path to a specific file may be supplied.  If no token is found, a
``ghtoken.GHTokenNotFound`` exception is raised.

.. code:: python

    ghtoken.ghtoken_from_environ() -> str

Retrieve a GitHub access token from environment variables as described above.
If no token is found, a ``ghtoken.GHTokenNotFound`` exception is raised.

.. code:: python

    ghtoken.ghtoken_from_gh() -> str

Retrieve a GitHub access token from the ``gh`` command as described above.  If
no token is found, a ``ghtoken.GHTokenNotFound`` exception is raised.

.. code:: python

    ghtoken.ghtoken_from_hub() -> str

Retrieve a GitHub access token from the ``hub`` configuration file as described
above.  If no token is found, a ``ghtoken.GHTokenNotFound`` exception is
raised.

.. code:: python

    ghtoken.ghtoken_from_hub_oauthtoken() -> str

Retrieve a GitHub access token from the ``hub.oauthtoken`` Git config option as
described above.  If no token is found, a ``ghtoken.GHTokenNotFound`` exception
is raised.


Command
=======

``ghtoken`` also provides a command of the same name for looking up a GitHub
token from the command line::

    ghtoken [<options>]

``ghtoken`` retrieves the local user's GitHub access token from local storage
and prints it.  If no token can be found, a message is printed to standard
error, and the command exits with a nonzero status.

Options
-------

-E FILE, --env FILE             Use the given file as the ``.env`` file source

--no-dotenv                     Do not consult a ``.env`` file

--no-environ                    Do not consult environment variables

--no-gh                         Do not consult ``gh``

--no-hub                        Do not consult ``hub`` configuration file

--no-hub-oauthtoken             Do not consult ``hub.oauthtoken`` Git config
                                option
