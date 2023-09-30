from __future__ import annotations
from pathlib import Path
from shlex import quote
import pytest
from ghtoken import GHTokenNotFound, ghtoken_from_dotenv


def write_dotenv(path: Path, values: dict[str, str]) -> None:
    with path.open("w") as fp:
        for k, v in values.items():
            print(f"{k}={quote(v)}", file=fp)


@pytest.mark.parametrize(
    "envvars,token",
    [
        ({}, None),
        ({"GITHUB_TOKEN": ""}, None),
        ({"GH_TOKEN": ""}, None),
        ({"GITHUB_TOKEN": " "}, " "),
        ({"GH_TOKEN": " "}, " "),
        ({"GITHUB_TOKEN": "my_token"}, "my_token"),
        ({"GH_TOKEN": "my_token"}, "my_token"),
        ({"GH_TOKEN": "my_token", "GITHUB_TOKEN": "my_other_token"}, "my_token"),
        ({"GH_TOKEN": "", "GITHUB_TOKEN": "my_other_token"}, "my_other_token"),
        ({"GH_TOKEN": " ", "GITHUB_TOKEN": "my_other_token"}, " "),
        ({"GH_TOKEN": "my_token", "GITHUB_TOKEN": ""}, "my_token"),
        ({"GH_TOKEN": "", "GITHUB_TOKEN": ""}, None),
    ],
)
def test_ghtoken_from_dotenv(
    envvars: dict[str, str],
    token: str | None,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.chdir(tmp_path)
    write_dotenv(Path(".env"), envvars)
    if token is not None:
        assert ghtoken_from_dotenv() == token
    else:
        with pytest.raises(GHTokenNotFound):
            ghtoken_from_dotenv()


@pytest.mark.parametrize(
    "envvars,token",
    [
        ({}, None),
        ({"GITHUB_TOKEN": ""}, None),
        ({"GH_TOKEN": ""}, None),
        ({"GITHUB_TOKEN": " "}, " "),
        ({"GH_TOKEN": " "}, " "),
        ({"GITHUB_TOKEN": "my_token"}, "my_token"),
        ({"GH_TOKEN": "my_token"}, "my_token"),
        ({"GH_TOKEN": "my_token", "GITHUB_TOKEN": "my_other_token"}, "my_token"),
        ({"GH_TOKEN": "", "GITHUB_TOKEN": "my_other_token"}, "my_other_token"),
        ({"GH_TOKEN": " ", "GITHUB_TOKEN": "my_other_token"}, " "),
        ({"GH_TOKEN": "my_token", "GITHUB_TOKEN": ""}, "my_token"),
        ({"GH_TOKEN": "", "GITHUB_TOKEN": ""}, None),
    ],
)
def test_ghtoken_from_custom_dotenv(
    envvars: dict[str, str],
    token: str | None,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.chdir(tmp_path)
    write_dotenv(Path(".env"), {"GH_TOKEN": "gh", "GITHUB_TOKEN": "github"})
    write_dotenv(Path("custom.env"), envvars)
    if token is not None:
        assert ghtoken_from_dotenv("custom.env") == token
    else:
        with pytest.raises(GHTokenNotFound):
            ghtoken_from_dotenv("custom.env")


def test_ghtoken_from_dotenv_not_exists(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.chdir(tmp_path)
    with pytest.raises(GHTokenNotFound):
        ghtoken_from_dotenv()


def test_ghtoken_from_custom_dotenv_not_exists(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.chdir(tmp_path)
    write_dotenv(Path(".env"), {"GH_TOKEN": "gh", "GITHUB_TOKEN": "github"})
    with pytest.raises(GHTokenNotFound):
        ghtoken_from_dotenv("custom.env")
