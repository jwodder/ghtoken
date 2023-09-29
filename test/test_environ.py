from __future__ import annotations
import pytest
from ghtoken import GitHubTokenNotFound, get_github_token_from_environ


@pytest.mark.parametrize(
    "envvars,token",
    [
        ({}, None),
        ({"GITHUB_TOKEN": ""}, None),
        ({"GH_TOKEN": ""}, None),
        ({"GITHUB_TOKEN": "my_token"}, "my_token"),
        ({"GH_TOKEN": "my_token"}, "my_token"),
        ({"GH_TOKEN": "my_token", "GITHUB_TOKEN": "my_other_token"}, "my_token"),
        ({"GH_TOKEN": "", "GITHUB_TOKEN": "my_other_token"}, "my_other_token"),
        ({"GH_TOKEN": "my_token", "GITHUB_TOKEN": ""}, "my_token"),
        ({"GH_TOKEN": "", "GITHUB_TOKEN": ""}, None),
    ],
)
def test_get_github_token_from_environ(
    envvars: dict[str, str], token: str | None, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv("GH_TOKEN", raising=False)
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    for k, v in envvars.items():
        monkeypatch.setenv(k, v)
    if token is not None:
        assert get_github_token_from_environ() == token
    else:
        with pytest.raises(GitHubTokenNotFound):
            get_github_token_from_environ()
