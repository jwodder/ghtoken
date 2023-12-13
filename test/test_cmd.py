from __future__ import annotations
from collections.abc import Callable
from pathlib import Path
import shutil
import sys
from typing import Any
import pytest
from ghtoken.__main__ import main

needs_gh = pytest.mark.skipif(shutil.which("gh") is None, reason="gh not installed")
needs_git = pytest.mark.skipif(shutil.which("git") is None, reason="git not installed")


def make_dotenv(tmp_path: Path, **_: Any) -> None:
    (tmp_path / ".env").write_text("GITHUB_TOKEN=dotenv_token\n", encoding="us-ascii")


def make_dotenv_custom(tmp_path: Path, **_: Any) -> None:
    (tmp_path / "custom.env").write_text(
        "GITHUB_TOKEN=dotenv_custom_token\n", encoding="us-ascii"
    )


def make_environ(monkeypatch: pytest.MonkeyPatch, **_: Any) -> None:
    monkeypatch.setenv("GITHUB_TOKEN", "environ_token")


def make_gh(tmp_home: Path, **_: Any) -> None:
    hosts_file = tmp_home / ".config" / "gh" / "hosts.yml"
    hosts_file.parent.mkdir(parents=True, exist_ok=True)
    hosts_file.write_text(
        "github.com:\n    oauth_token: gh_token\n    user: myself\n",
        encoding="us-ascii",
    )


def make_hub(tmp_home: Path, **_: Any) -> None:
    (tmp_home / ".config").mkdir(exist_ok=True)
    (tmp_home / ".config" / "hub").write_text(
        "github.com:\n- oauth_token: hub_token\n",
        encoding="us-ascii",
    )


def make_hub_oauthtoken(tmp_home: Path, **_: Any) -> None:
    (tmp_home / ".gitconfig").write_text(
        "[hub]\noauthtoken = hub_oauthtoken_token\n",
        encoding="us-ascii",
    )


@pytest.mark.parametrize(
    "opts,makers,token",
    [
        ([], [], None),
        (
            [],
            [make_dotenv, make_environ, make_gh, make_hub, make_hub_oauthtoken],
            "dotenv_token",
        ),
        (
            ["--env", "custom.env"],
            [make_dotenv_custom, make_environ, make_gh, make_hub, make_hub_oauthtoken],
            "dotenv_custom_token",
        ),
        (
            ["--env", "custom.env"],
            [make_dotenv, make_environ, make_gh, make_hub, make_hub_oauthtoken],
            "environ_token",
        ),
        (
            [],
            [make_environ, make_gh, make_hub, make_hub_oauthtoken],
            "environ_token",
        ),
        (
            ["--no-dotenv"],
            [make_dotenv, make_environ, make_gh, make_hub, make_hub_oauthtoken],
            "environ_token",
        ),
        pytest.param(
            ["--no-dotenv"],
            [make_dotenv, make_gh, make_hub, make_hub_oauthtoken],  # type: ignore[list-item]
            "gh_token",
            marks=[needs_gh],
        ),
        pytest.param(
            [],
            [make_gh, make_hub, make_hub_oauthtoken],
            "gh_token",
            marks=[needs_gh],
        ),
        (
            ["--no-dotenv", "--no-environ"],
            [make_dotenv, make_hub, make_hub_oauthtoken],  # type: ignore[list-item]
            "hub_token",
        ),
        (
            ["--no-dotenv", "--no-environ", "--no-gh"],
            [make_dotenv, make_environ, make_gh, make_hub, make_hub_oauthtoken],
            "hub_token",
        ),
        (
            [],
            [make_hub, make_hub_oauthtoken],
            "hub_token",
        ),
        pytest.param(
            ["--no-dotenv", "--no-environ", "--no-gh"],
            [make_dotenv, make_environ, make_gh, make_hub_oauthtoken],
            "hub_oauthtoken_token",
            marks=[needs_git],
        ),
        pytest.param(
            ["--no-dotenv", "--no-environ", "--no-gh", "--no-hub"],
            [make_dotenv, make_environ, make_gh, make_hub, make_hub_oauthtoken],
            "hub_oauthtoken_token",
            marks=[needs_git],
        ),
        pytest.param(
            [],
            [make_hub_oauthtoken],
            "hub_oauthtoken_token",
            marks=[needs_git],
        ),
        (
            ["--no-dotenv", "--no-environ", "--no-gh", "--no-hub"],
            [make_dotenv, make_environ, make_gh, make_hub],
            None,
        ),
        (
            [
                "--no-dotenv",
                "--no-environ",
                "--no-gh",
                "--no-hub",
                "--no-hub-oauthtoken",
            ],
            [make_dotenv, make_environ, make_gh, make_hub, make_hub_oauthtoken],
            None,
        ),
    ],
)
def test_get_github_token(
    opts: list[str],
    makers: list[Callable],
    token: str | None,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
    tmp_home: Path,
    tmp_path: Path,
) -> None:
    monkeypatch.delenv("GH_TOKEN", raising=False)
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    monkeypatch.chdir(tmp_path)
    for m in makers:
        m(monkeypatch=monkeypatch, tmp_home=tmp_home, tmp_path=tmp_path)
    monkeypatch.setattr(sys, "argv", ["ghtoken"] + opts)
    if token is not None:
        main()
        out, err = capsys.readouterr()
        assert out == f"{token}\n"
        assert err == ""
    else:
        with pytest.raises(SystemExit) as excinfo:
            main()
        assert excinfo.value.args == (1,)
        out, err = capsys.readouterr()
        assert out == ""
        assert err == "GitHub access token not found\n"
