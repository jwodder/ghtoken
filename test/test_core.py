from __future__ import annotations
from collections.abc import Callable
from pathlib import Path
import shutil
from typing import Any
import pytest
from ghtoken import GHTokenNotFound, get_ghtoken

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
    "kwargs,makers,token",
    [
        ({}, [], None),
        (
            {},
            [make_dotenv, make_environ, make_gh, make_hub, make_hub_oauthtoken],
            "dotenv_token",
        ),
        (
            {"dotenv": "custom.env"},
            [make_dotenv_custom, make_environ, make_gh, make_hub, make_hub_oauthtoken],
            "dotenv_custom_token",
        ),
        (
            {"dotenv": "custom.env"},
            [make_dotenv, make_environ, make_gh, make_hub, make_hub_oauthtoken],
            "environ_token",
        ),
        (
            {},
            [make_environ, make_gh, make_hub, make_hub_oauthtoken],
            "environ_token",
        ),
        (
            {"dotenv": False},
            [make_dotenv, make_environ, make_gh, make_hub, make_hub_oauthtoken],
            "environ_token",
        ),
        pytest.param(
            {"dotenv": False},
            [make_dotenv, make_gh, make_hub, make_hub_oauthtoken],  # type: ignore[list-item]
            "gh_token",
            marks=[needs_gh],
        ),
        pytest.param(
            {},
            [make_gh, make_hub, make_hub_oauthtoken],
            "gh_token",
            marks=[needs_gh],
        ),
        (
            {"dotenv": False, "environ": False},
            [make_dotenv, make_hub, make_hub_oauthtoken],  # type: ignore[list-item]
            "hub_token",
        ),
        (
            {"dotenv": False, "environ": False, "gh": False},
            [make_dotenv, make_environ, make_gh, make_hub, make_hub_oauthtoken],
            "hub_token",
        ),
        (
            {},
            [make_hub, make_hub_oauthtoken],
            "hub_token",
        ),
        pytest.param(
            {"dotenv": False, "environ": False, "gh": False},
            [make_dotenv, make_environ, make_gh, make_hub_oauthtoken],
            "hub_oauthtoken_token",
            marks=[needs_git],
        ),
        pytest.param(
            {"dotenv": False, "environ": False, "gh": False, "hub": False},
            [make_dotenv, make_environ, make_gh, make_hub, make_hub_oauthtoken],
            "hub_oauthtoken_token",
            marks=[needs_git],
        ),
        pytest.param(
            {},
            [make_hub_oauthtoken],
            "hub_oauthtoken_token",
            marks=[needs_git],
        ),
        (
            {"dotenv": False, "environ": False, "gh": False, "hub": False},
            [make_dotenv, make_environ, make_gh, make_hub],
            None,
        ),
        (
            {
                "dotenv": False,
                "environ": False,
                "gh": False,
                "hub": False,
                "hub_oauthtoken": False,
            },
            [make_dotenv, make_environ, make_gh, make_hub, make_hub_oauthtoken],
            None,
        ),
    ],
)
def test_get_github_token(
    kwargs: dict[str, Any],
    makers: list[Callable],
    token: str | None,
    monkeypatch: pytest.MonkeyPatch,
    tmp_home: Path,
    tmp_path: Path,
) -> None:
    monkeypatch.delenv("GH_TOKEN", raising=False)
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    monkeypatch.chdir(tmp_path)
    for m in makers:
        m(monkeypatch=monkeypatch, tmp_home=tmp_home, tmp_path=tmp_path)
    if token is not None:
        assert get_ghtoken(**kwargs) == token
    else:
        with pytest.raises(GHTokenNotFound):
            get_ghtoken(**kwargs)
