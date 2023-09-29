from __future__ import annotations
from pathlib import Path
import shutil
import subprocess
from typing import Any
import pytest
from ghtoken import GitHubTokenNotFound, get_github_token_for_git_hub

pytestmark = pytest.mark.skipif(shutil.which("git") is None, reason="git not installed")


def test_git_hub_no_token(tmp_home: Path) -> None:  # noqa: U100
    with pytest.raises(GitHubTokenNotFound):
        get_github_token_for_git_hub()


def test_git_hub(tmp_home: Path) -> None:
    (tmp_home / ".gitconfig").write_text(
        "[hub]\noauthtoken = my_token\n",
        encoding="us-ascii",
    )
    assert get_github_token_for_git_hub() == "my_token"


def test_git_hub_empty_token(tmp_home: Path) -> None:
    (tmp_home / ".gitconfig").write_text(
        "[hub]\noauthtoken = \n",
        encoding="us-ascii",
    )
    with pytest.raises(GitHubTokenNotFound):
        get_github_token_for_git_hub()


def test_git_hub_whitespace_token(tmp_home: Path) -> None:
    (tmp_home / ".gitconfig").write_text(
        '[hub]\noauthtoken = " "\n',
        encoding="us-ascii",
    )
    assert get_github_token_for_git_hub() == " "


def test_git_hub_default_baseurl(tmp_home: Path) -> None:
    (tmp_home / ".gitconfig").write_text(
        "[hub]\nbaseurl = https://api.github.com\noauthtoken = my_token\n",
        encoding="us-ascii",
    )
    assert get_github_token_for_git_hub() == "my_token"


def test_git_hub_custom_baseurl(tmp_home: Path) -> None:
    (tmp_home / ".gitconfig").write_text(
        "[hub]\nbaseurl = https://example.com/github\noauthtoken = my_token\n",
        encoding="us-ascii",
    )
    with pytest.raises(GitHubTokenNotFound):
        get_github_token_for_git_hub()


@pytest.mark.parametrize(
    "stdout,token",
    [
        ("my_token\n", "my_token"),
        ("\n", ""),
        (" \n", ""),
    ],
)
def test_git_hub_shell_token(
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
    assert get_github_token_for_git_hub() == token
    assert shells == [("foo --bar baz",)]


def test_git_hub_shell_error(monkeypatch: pytest.MonkeyPatch, tmp_home: Path) -> None:
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
        get_github_token_for_git_hub()
    assert shells == [("foo --bar baz",)]


def test_git_hub_custom_baseurl_shell_not_run(
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
    with pytest.raises(GitHubTokenNotFound):
        get_github_token_for_git_hub()
    assert shells == []
