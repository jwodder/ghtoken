from __future__ import annotations
import pytest
from ghtoken import GHTokenNotFound, ghtoken_from_environ


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
def test_ghtoken_from_environ(
    envvars: dict[str, str], token: str | None, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv("GH_TOKEN", raising=False)
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    for k, v in envvars.items():
        monkeypatch.setenv(k, v)
    if token is not None:
        assert ghtoken_from_environ() == token
    else:
        with pytest.raises(GHTokenNotFound):
            ghtoken_from_environ()
