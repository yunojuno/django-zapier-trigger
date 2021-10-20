from __future__ import annotations

import pytest
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.utils.timezone import now as tz_now
from freezegun import freeze_time

from zapier.exceptions import JsonResponseError, TokenScopeError
from zapier.models import RequestLog, ZapierToken, encode_timestamp


@pytest.mark.django_db
class TestZapierToken:
    def test_timestamps(self, zapier_token: ZapierToken) -> None:
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
        ],
    )
    def test_has_scope(
        self,
        zapier_token: ZapierToken,
        scopes: list[str],
        scope: str,
        has_scope: bool,
    ) -> None:
        zapier_token.api_scopes = scopes
        assert zapier_token.has_scope(scope) == has_scope

    def test_has_scope__error(self, zapier_token: ZapierToken) -> None:
        with pytest.raises(ValueError):
            zapier_token.has_scope("*")

    @pytest.mark.parametrize(
        "scopes,scope,error",
        [
            (["foo"], "", ValueError),
            (["foo"], "*", None),
            (["foo"], "foo", None),
            (["foo"], "bar", TokenScopeError),
        ],
    )
    def test_check_scope__error(
        self,
        zapier_token: ZapierToken,
        scopes: list[str],
        scope: str,
        error: type[Exception] | None,
    ) -> None:
        zapier_token.api_scopes = scopes
        if error:
            with pytest.raises(error):
                zapier_token.check_scope(scope)
        else:
            zapier_token.check_scope(scope)

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
        zapier_token = ZapierToken.objects.create(user=user, api_scopes=scopes_before)
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
        zapier_token = ZapierToken.objects.create(user=user, api_scopes=scopes_before)
        if isinstance(remove_scope, str):
            zapier_token.remove_scope(remove_scope)
        else:
            zapier_token.remove_scopes(remove_scope)
        assert set(zapier_token.api_scopes) == set(scopes_after)

    @pytest.mark.parametrize("scopes", [["*"], ["*", "foo"]])
    def test_set_scopes(self, zapier_token: ZapierToken, scopes: list[str]) -> None:
        zapier_token.set_scopes(scopes)
        assert zapier_token.api_scopes == scopes
        zapier_token.refresh_from_db()
        assert zapier_token.api_scopes == scopes

    @pytest.mark.parametrize(
        "request_log,result",
        [
            (
                {"foo": ("2021-10-14T19:32:20", 0, None)},
                RequestLog("2021-10-14T19:32:20", 0, None),
            ),
            ({"bar": ("2021-10-14T19:32:20", 1, 1)}, None),
            ({}, None),
        ],
    )
    def test_get_request_log(
        self,
        zapier_token: ZapierToken,
        request_log: dict,
        result: RequestLog | None,
    ) -> None:
        zapier_token.request_log = request_log
        assert zapier_token.get_request_log("foo") == result

    # tricky to parametrize, so this is three-in-one as the order is crucial
    def test_log_scope_request(self, zapier_token: ZapierToken) -> None:
        assert zapier_token.request_log == {}

        # first request - starts with a blank
        now1 = tz_now()
        with freeze_time(now1):
            timestamp1 = encode_timestamp(now1)
            response = JsonResponse([{"id": 1}], safe=False)
            zapier_token.log_scope_request("foo", response)
        # pre-serialized form is the actual date
        assert zapier_token.request_log == {"foo": [timestamp1, 1, 1]}
        zapier_token.refresh_from_db()
        assert zapier_token.request_log == {"foo": [timestamp1, 1, 1]}

        # second request has multiple items
        now2 = tz_now()
        with freeze_time(now2):
            timestamp2 = encode_timestamp(now2)
            response = JsonResponse([{"id": 3}, {"id": 2}], safe=False)
            zapier_token.log_scope_request("foo", response)
        assert zapier_token.request_log == {"foo": [timestamp2, 2, 3]}
        zapier_token.refresh_from_db()

        # third request returns nothing - ensure max_id is retained
        now3 = tz_now()
        with freeze_time(now3):
            timestamp3 = encode_timestamp(now3)
            response = JsonResponse([], safe=False)
            zapier_token.log_scope_request("foo", response)
        assert zapier_token.request_log == {"foo": [timestamp3, 0, 3]}
        zapier_token.refresh_from_db()

        # fourth request is another scope
        now4 = tz_now()
        with freeze_time(now4):
            timestamp4 = encode_timestamp(now4)
            response = JsonResponse([], safe=False)
            zapier_token.log_scope_request("bar", response)
        assert zapier_token.request_log == {
            "foo": [timestamp3, 0, 3],
            "bar": [timestamp4, 0, None],
        }

    def test_log_scope_request__unparseable_json(
        self, zapier_token: ZapierToken
    ) -> None:
        with pytest.raises(JsonResponseError):
            response = HttpResponse("foo")
            zapier_token.log_scope_request("foo", response)
        assert zapier_token.request_log == {}

    @pytest.mark.parametrize(
        "content",
        [
            "ok",
            {"id": 0},
            {"id": "foo"},
            [{"foo": "bar"}],
        ],
    )
    def test_log_scope_request__invalid_json(
        self, content, zapier_token: ZapierToken
    ) -> None:
        # invalid json
        with pytest.raises(JsonResponseError):
            response = JsonResponse(content, safe=False)
            zapier_token.log_scope_request("foo", response)
        assert zapier_token.request_log == {}

    def test_refresh(self, zapier_token: ZapierToken) -> None:
        """Test refresh method updates the api_token."""
        old_token = zapier_token.api_token
        zapier_token.refresh()
        assert zapier_token.api_token != old_token
        zapier_token.refresh_from_db()
        assert zapier_token.api_token != old_token

    def test_reset(self, zapier_token: ZapierToken) -> None:
        """Test reset method clears out request_log."""
        response = JsonResponse([{"id": 1}], safe=False)
        zapier_token.log_scope_request("foo", response)
        assert zapier_token.request_log
        zapier_token.reset()
        assert not zapier_token.request_log
        zapier_token.refresh_from_db()
        assert not zapier_token.request_log

    def test_revoke(self, zapier_token: ZapierToken) -> None:
        """Test revoke method removes all scopes."""
        old_scopes = zapier_token.api_scopes
        assert old_scopes
        zapier_token.revoke()
        assert zapier_token.api_scopes == []
        zapier_token.refresh_from_db()
        assert zapier_token.api_scopes == []
