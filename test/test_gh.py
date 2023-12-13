from __future__ import annotations
from pathlib import Path
import shutil
import pytest
from ghtoken import GHTokenNotFound, ghtoken_from_gh

pytestmark = pytest.mark.skipif(shutil.which("gh") is None, reason="gh not installed")


def test_gh_no_token(
    monkeypatch: pytest.MonkeyPatch,
    tmp_home: Path,  # noqa: U100
) -> None:
    monkeypatch.delenv("GH_TOKEN", raising=False)
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    with pytest.raises(GHTokenNotFound):
        ghtoken_from_gh()


def test_gh(monkeypatch: pytest.MonkeyPatch, tmp_home: Path) -> None:
    monkeypatch.delenv("GH_TOKEN", raising=False)
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    hosts_file = tmp_home / ".config" / "gh" / "hosts.yml"
    hosts_file.parent.mkdir(parents=True, exist_ok=True)
    hosts_file.write_text(
        "github.com:\n    oauth_token: my_token\n    user: myself\n",
        encoding="us-ascii",
    )
    assert ghtoken_from_gh() == "my_token"


def test_gh_whitespace_token(monkeypatch: pytest.MonkeyPatch, tmp_home: Path) -> None:
    monkeypatch.delenv("GH_TOKEN", raising=False)
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    hosts_file = tmp_home / ".config" / "gh" / "hosts.yml"
    hosts_file.parent.mkdir(parents=True, exist_ok=True)
    hosts_file.write_text(
        "github.com:\n    oauth_token: ' '\n    user: myself\n",
        encoding="us-ascii",
    )
    assert ghtoken_from_gh() == " "
