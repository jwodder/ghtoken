from __future__ import annotations
from pathlib import Path
import pytest
from ghtoken import GHTokenNotFound, ghtoken_from_hub


def test_hub(tmp_home: Path) -> None:
    (tmp_home / ".config").mkdir()
    (tmp_home / ".config" / "hub").write_text(
        "github.com:\n- oauth_token: my_token\n",
        encoding="us-ascii",
    )
    assert ghtoken_from_hub() == "my_token"


def test_hub_whitespace(tmp_home: Path) -> None:
    (tmp_home / ".config").mkdir()
    (tmp_home / ".config" / "hub").write_text(
        "github.com:\n- oauth_token: ' '\n",
        encoding="us-ascii",
    )
    assert ghtoken_from_hub() == " "


def test_hub_no_config(tmp_home: Path) -> None:  # noqa: U100
    with pytest.raises(GHTokenNotFound):
        ghtoken_from_hub()


@pytest.mark.parametrize(
    "cfg",
    [
        "",
        "github.com:\n- oauth_token:\n",
        "github.com:\n- oauth_token: 42\n",
        "example.com:\n- oauth_token: my_token\n",
        "github.com:\n oauth_token: my_token\n",
        "github.com: []\n",
        "github.com:\n - my_token\n",
        "github.com:\n- token: my_token\n",
        "- oauth_token: my_token\n",
    ],
)
def test_hub_invalid_config(cfg: str, tmp_home: Path) -> None:
    (tmp_home / ".config").mkdir()
    (tmp_home / ".config" / "hub").write_text(cfg, encoding="us-ascii")
    with pytest.raises(GHTokenNotFound):
        ghtoken_from_hub()


def test_hub_hub_config(monkeypatch: pytest.MonkeyPatch, tmp_home: Path) -> None:
    monkeypatch.setenv("HUB_CONFIG", str(tmp_home / "hub.yaml"))
    (tmp_home / "hub.yaml").write_text(
        "github.com:\n- oauth_token: hub_config_token\n",
        encoding="us-ascii",
    )
    (tmp_home / ".config").mkdir()
    (tmp_home / ".config" / "hub").write_text(
        "github.com:\n- oauth_token: default_token\n",
        encoding="us-ascii",
    )
    assert ghtoken_from_hub() == "hub_config_token"


def test_hub_hub_config_not_exists(
    monkeypatch: pytest.MonkeyPatch, tmp_home: Path
) -> None:
    monkeypatch.setenv("HUB_CONFIG", str(tmp_home / "hub.yaml"))
    (tmp_home / ".config").mkdir()
    (tmp_home / ".config" / "hub").write_text(
        "github.com:\n- oauth_token: default_token\n",
        encoding="us-ascii",
    )
    with pytest.raises(GHTokenNotFound):
        ghtoken_from_hub()


def test_hub_xdg_config_home(monkeypatch: pytest.MonkeyPatch, tmp_home: Path) -> None:
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_home / "xdg-config"))
    (tmp_home / "xdg-config").mkdir()
    (tmp_home / "xdg-config" / "hub").write_text(
        "github.com:\n- oauth_token: xdg_config_token\n",
        encoding="us-ascii",
    )
    (tmp_home / ".config").mkdir()
    (tmp_home / ".config" / "hub").write_text(
        "github.com:\n- oauth_token: default_token\n",
        encoding="us-ascii",
    )
    assert ghtoken_from_hub() == "xdg_config_token"


def test_hub_xdg_config_home_not_exists(
    monkeypatch: pytest.MonkeyPatch, tmp_home: Path
) -> None:
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_home / "xdg-config"))
    (tmp_home / ".config").mkdir()
    (tmp_home / ".config" / "hub").write_text(
        "github.com:\n- oauth_token: default_token\n",
        encoding="us-ascii",
    )
    with pytest.raises(GHTokenNotFound):
        ghtoken_from_hub()


def test_hub_hub_config_xdg_config_home(
    monkeypatch: pytest.MonkeyPatch, tmp_home: Path
) -> None:
    monkeypatch.setenv("HUB_CONFIG", str(tmp_home / "hub.yaml"))
    (tmp_home / "hub.yaml").write_text(
        "github.com:\n- oauth_token: hub_config_token\n",
        encoding="us-ascii",
    )
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_home / "xdg-config"))
    (tmp_home / "xdg-config").mkdir()
    (tmp_home / "xdg-config" / "hub").write_text(
        "github.com:\n- oauth_token: xdg_config_token\n",
        encoding="us-ascii",
    )
    (tmp_home / ".config").mkdir()
    (tmp_home / ".config" / "hub").write_text(
        "github.com:\n- oauth_token: default_token\n",
        encoding="us-ascii",
    )
    assert ghtoken_from_hub() == "hub_config_token"


def test_hub_hub_config_not_exists_xdg_config_home(
    monkeypatch: pytest.MonkeyPatch, tmp_home: Path
) -> None:
    monkeypatch.setenv("HUB_CONFIG", str(tmp_home / "hub.yaml"))
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_home / "xdg-config"))
    (tmp_home / "xdg-config").mkdir()
    (tmp_home / "xdg-config" / "hub").write_text(
        "github.com:\n- oauth_token: xdg_config_token\n",
        encoding="us-ascii",
    )
    (tmp_home / ".config").mkdir()
    (tmp_home / ".config" / "hub").write_text(
        "github.com:\n- oauth_token: default_token\n",
        encoding="us-ascii",
    )
    with pytest.raises(GHTokenNotFound):
        ghtoken_from_hub()


def test_hub_xdg_config_dirs(
    monkeypatch: pytest.MonkeyPatch, tmp_home: Path, tmp_path: Path  # noqa: U100
) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("XDG_CONFIG_DIRS", "foo:bar:baz")
    Path("bar").mkdir()
    Path("bar", "hub").write_text(
        "github.com:\n- oauth_token: bar_token\n",
        encoding="us-ascii",
    )
    Path("baz").mkdir()
    Path("baz", "hub").write_text(
        "github.com:\n- oauth_token: baz_token\n",
        encoding="us-ascii",
    )
    assert ghtoken_from_hub() == "bar_token"


def test_hub_xdg_config_dirs_default_exists(
    monkeypatch: pytest.MonkeyPatch, tmp_home: Path, tmp_path: Path
) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("XDG_CONFIG_DIRS", "foo:bar:baz")
    Path("bar").mkdir()
    Path("bar", "hub").write_text(
        "github.com:\n- oauth_token: bar_token\n",
        encoding="us-ascii",
    )
    Path("baz").mkdir()
    Path("baz", "hub").write_text(
        "github.com:\n- oauth_token: baz_token\n",
        encoding="us-ascii",
    )
    (tmp_home / ".config").mkdir()
    (tmp_home / ".config" / "hub").write_text(
        "github.com:\n- oauth_token: default_token\n",
        encoding="us-ascii",
    )
    assert ghtoken_from_hub() == "default_token"


def test_hub_xdg_config_home_xdg_config_dirs(
    monkeypatch: pytest.MonkeyPatch, tmp_home: Path, tmp_path: Path
) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_home / "xdg-config"))
    (tmp_home / "xdg-config").mkdir()
    (tmp_home / "xdg-config" / "hub").write_text(
        "github.com:\n- oauth_token: xdg_config_token\n",
        encoding="us-ascii",
    )
    monkeypatch.setenv("XDG_CONFIG_DIRS", "foo:bar:baz")
    Path("bar").mkdir()
    Path("bar", "hub").write_text(
        "github.com:\n- oauth_token: bar_token\n",
        encoding="us-ascii",
    )
    Path("baz").mkdir()
    Path("baz", "hub").write_text(
        "github.com:\n- oauth_token: baz_token\n",
        encoding="us-ascii",
    )
    (tmp_home / ".config").mkdir()
    (tmp_home / ".config" / "hub").write_text(
        "github.com:\n- oauth_token: default_token\n",
        encoding="us-ascii",
    )
    assert ghtoken_from_hub() == "xdg_config_token"


def test_hub_xdg_config_home_not_exists_xdg_config_dirs(
    monkeypatch: pytest.MonkeyPatch, tmp_home: Path, tmp_path: Path
) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_home / "xdg-config"))
    monkeypatch.setenv("XDG_CONFIG_DIRS", "foo:bar:baz")
    Path("bar").mkdir()
    Path("bar", "hub").write_text(
        "github.com:\n- oauth_token: bar_token\n",
        encoding="us-ascii",
    )
    Path("baz").mkdir()
    Path("baz", "hub").write_text(
        "github.com:\n- oauth_token: baz_token\n",
        encoding="us-ascii",
    )
    (tmp_home / ".config").mkdir()
    (tmp_home / ".config" / "hub").write_text(
        "github.com:\n- oauth_token: default_token\n",
        encoding="us-ascii",
    )
    assert ghtoken_from_hub() == "bar_token"


def test_hub_invalid_hub_config_valid_default(
    monkeypatch: pytest.MonkeyPatch, tmp_home: Path
) -> None:
    monkeypatch.setenv("HUB_CONFIG", str(tmp_home / "hub.yaml"))
    (tmp_home / "hub.yaml").write_text("garbage\n", encoding="us-ascii")
    (tmp_home / ".config").mkdir()
    (tmp_home / ".config" / "hub").write_text(
        "github.com:\n- oauth_token: default_token\n",
        encoding="us-ascii",
    )
    with pytest.raises(GHTokenNotFound):
        ghtoken_from_hub()


def test_hub_xdg_config_home_invalid_xdg_config_dirs(
    monkeypatch: pytest.MonkeyPatch, tmp_home: Path, tmp_path: Path
) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_home / "xdg-config"))
    (tmp_home / "xdg-config").mkdir()
    (tmp_home / "xdg-config" / "hub").write_text("garbage\n", encoding="us-ascii")
    monkeypatch.setenv("XDG_CONFIG_DIRS", "foo:bar:baz")
    Path("bar").mkdir()
    Path("bar", "hub").write_text(
        "github.com:\n- oauth_token: bar_token\n",
        encoding="us-ascii",
    )
    Path("baz").mkdir()
    Path("baz", "hub").write_text(
        "github.com:\n- oauth_token: baz_token\n",
        encoding="us-ascii",
    )
    (tmp_home / ".config").mkdir()
    (tmp_home / ".config" / "hub").write_text(
        "github.com:\n- oauth_token: default_token\n",
        encoding="us-ascii",
    )
    with pytest.raises(GHTokenNotFound):
        ghtoken_from_hub()
