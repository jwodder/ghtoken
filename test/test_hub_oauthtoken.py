from __future__ import annotations
from pathlib import Path
import shutil
import subprocess
from typing import Any
import pytest
from ghtoken import GHTokenNotFound, ghtoken_from_hub_oauthtoken

pytestmark = pytest.mark.skipif(shutil.which("git") is None, reason="git not installed")


def test_hub_oauthtoken_no_token(tmp_home: Path) -> None:  # noqa: U100
    with pytest.raises(GHTokenNotFound):
        ghtoken_from_hub_oauthtoken()


def test_hub_oauthtoken(tmp_home: Path) -> None:
    (tmp_home / ".gitconfig").write_text(
        "[hub]\noauthtoken = my_token\n",
        encoding="us-ascii",
    )
    assert ghtoken_from_hub_oauthtoken() == "my_token"


def test_hub_oauthtoken_empty_token(tmp_home: Path) -> None:
    (tmp_home / ".gitconfig").write_text(
        "[hub]\noauthtoken = \n",
        encoding="us-ascii",
    )
    with pytest.raises(GHTokenNotFound):
        ghtoken_from_hub_oauthtoken()


def test_hub_oauthtoken_whitespace_token(tmp_home: Path) -> None:
    (tmp_home / ".gitconfig").write_text(
        '[hub]\noauthtoken = " "\n',
        encoding="us-ascii",
    )
    assert ghtoken_from_hub_oauthtoken() == " "


def test_hub_oauthtoken_default_baseurl(tmp_home: Path) -> None:
    (tmp_home / ".gitconfig").write_text(
        "[hub]\nbaseurl = https://api.github.com\noauthtoken = my_token\n",
        encoding="us-ascii",
    )
    assert ghtoken_from_hub_oauthtoken() == "my_token"


def test_hub_oauthtoken_custom_baseurl(tmp_home: Path) -> None:
    (tmp_home / ".gitconfig").write_text(
        "[hub]\nbaseurl = https://example.com/github\noauthtoken = my_token\n",
        encoding="us-ascii",
    )
    with pytest.raises(GHTokenNotFound):
        ghtoken_from_hub_oauthtoken()


@pytest.mark.parametrize(
    "stdout,token",
    [
        ("my_token\n", "my_token"),
        ("\n", ""),
        (" \n", ""),
    ],
)
def test_hub_oauthtoken_shell_token(
    stdout: str, token: str, monkeypatch: pytest.MonkeyPatch, tmp_home: Path
) -> None:
    from subprocess import run

    shells = []

    def mock_run(*args: Any, **kwargs: Any) -> subprocess.CompletedProcess:
        if kwargs.get("shell"):
            shells.append(args)
            return subprocess.CompletedProcess(
                args=args,
                returncode=0,
                stdout=stdout,
                stderr=None,
            )
        else:
            return run(*args, **kwargs)

    (tmp_home / ".gitconfig").write_text(
        "[hub]\noauthtoken = !foo --bar baz\n",
        encoding="us-ascii",
    )
    monkeypatch.setattr(subprocess, "run", mock_run)
    assert ghtoken_from_hub_oauthtoken() == token
    assert shells == [("foo --bar baz",)]


def test_hub_oauthtoken_shell_error(
    monkeypatch: pytest.MonkeyPatch, tmp_home: Path
) -> None:
    from subprocess import run

    shells = []

    def mock_run(*args: Any, **kwargs: Any) -> subprocess.CompletedProcess:
        if kwargs.get("shell"):
            shells.append(args)
            raise subprocess.CalledProcessError(
                cmd=args,
                returncode=1,
                output="my_token\n",
                stderr=None,
            )
        else:
            return run(*args, **kwargs)

    (tmp_home / ".gitconfig").write_text(
        "[hub]\noauthtoken = !foo --bar baz\n",
        encoding="us-ascii",
    )
    monkeypatch.setattr(subprocess, "run", mock_run)
    with pytest.raises(subprocess.CalledProcessError):
        ghtoken_from_hub_oauthtoken()
    assert shells == [("foo --bar baz",)]


def test_hub_oauthtoken_custom_baseurl_shell_not_run(
    monkeypatch: pytest.MonkeyPatch, tmp_home: Path
) -> None:
    from subprocess import run

    shells = []

    def mock_run(*args: Any, **kwargs: Any) -> subprocess.CompletedProcess:
        if kwargs.get("shell"):
            shells.append(args)
            return subprocess.CompletedProcess(
                args=args,
                returncode=0,
                stdout="my_token\n",
                stderr=None,
            )
        else:
            return run(*args, **kwargs)

    (tmp_home / ".gitconfig").write_text(
        (
            "[hub]\n"
            "baseurl = https://example.com/github\n"
            "oauthtoken = !foo --bar baz\n"
        ),
        encoding="us-ascii",
    )
    monkeypatch.setattr(subprocess, "run", mock_run)
    with pytest.raises(GHTokenNotFound):
        ghtoken_from_hub_oauthtoken()
    assert shells == []
