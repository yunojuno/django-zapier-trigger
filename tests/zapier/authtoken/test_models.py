from __future__ import annotations

import pytest
from django.conf import settings

from zapier.authtoken.models import AuthToken


@pytest.mark.django_db
class TestAuthToken:
    def test_timestamps(self, zapier_token: AuthToken) -> None:
        assert zapier_token.created_at
        assert zapier_token.created_at == zapier_token.last_updated_at
        zapier_token.save()
        assert zapier_token.created_at < zapier_token.last_updated_at

    @pytest.mark.parametrize(
        "scopes,scope,has_scope",
        [
            (["*"], "foo", True),
            (["*", "-foo"], "foo", False),
            (["*", "foo"], "foo", True),
            (["foo"], "foo", True),
            (["foo", "bar"], "foo", True),
            (["foo", "bar"], AuthToken.ZAPIER_TOKEN_CHECK_SCOPE, True),
        ],
    )
    def test_has_scope(
        self,
        zapier_token: AuthToken,
        scopes: list[str],
        scope: str,
        has_scope: bool,
    ) -> None:
        zapier_token.api_scopes = scopes
        assert zapier_token.has_scope(scope) == has_scope

    def test_has_scope__error(self, zapier_token: AuthToken) -> None:
        with pytest.raises(ValueError):
            zapier_token.has_scope("*")

    @pytest.mark.parametrize(
        "scopes_before,add_scope,scopes_after",
        [
            (["*"], "foo", ["*", "foo"]),
            (["foo"], "bar", ["foo", "bar"]),
            (["foo"], "foo", ["foo"]),
            (["foo"], ["foo", "bar"], ["foo", "bar"]),
        ],
    )
    def test_add_scopes(
        self,
        user: settings.AUTH_USER_MODEL,
        scopes_before: list[str],
        add_scope: str | list,
        scopes_after: list[str],
    ) -> None:
        zapier_token = AuthToken.objects.create(user=user, api_scopes=scopes_before)
        if isinstance(add_scope, str):
            zapier_token.add_scope(add_scope)
        else:
            zapier_token.add_scopes(add_scope)
        assert set(zapier_token.api_scopes) == set(scopes_after)

    @pytest.mark.parametrize(
        "scopes_before,remove_scope,scopes_after",
        [
            (["*"], "foo", ["*"]),
            (["foo"], "bar", ["foo"]),
            (["foo"], "foo", []),
            (["foo", "bar"], ["foo"], ["bar"]),
            (["foo", "bar"], ["foo", "bar", "baz"], []),
        ],
    )
    def test_remove_scopes(
        self,
        user: settings.AUTH_USER_MODEL,
        scopes_before: list[str],
        remove_scope: str,
        scopes_after: list[str],
    ) -> None:
        zapier_token = AuthToken.objects.create(user=user, api_scopes=scopes_before)
        if isinstance(remove_scope, str):
            zapier_token.remove_scope(remove_scope)
        else:
            zapier_token.remove_scopes(remove_scope)
        assert set(zapier_token.api_scopes) == set(scopes_after)

    @pytest.mark.parametrize("scopes", [["*"], ["*", "foo"]])
    def test_set_scopes(self, zapier_token: AuthToken, scopes: list[str]) -> None:
        zapier_token.set_scopes(scopes)
        assert zapier_token.api_scopes == scopes
        zapier_token.refresh_from_db()
        assert zapier_token.api_scopes == scopes
