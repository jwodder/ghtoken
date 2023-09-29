from __future__ import annotations
import pytest
from ghtoken import get_github_token_from_environ


@pytest.mark.parametrize(
    "envvars,token",
    [
        ({"GITHUB_TOKEN": "my_token"}, "my_token"),
        ({"GH_TOKEN": "my_token"}, "my_token"),
        ({"GH_TOKEN": "my_token", "GITHUB_TOKEN": "my_other_token"}, "my_token"),
    ],
)
def test_get_github_token_from_environ(
    envvars: dict[str, str], token: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv("GH_TOKEN", raising=False)
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    for k, v in envvars.items():
        monkeypatch.setenv(k, v)
    assert get_github_token_from_environ() == token
