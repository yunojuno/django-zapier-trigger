import json
from datetime import datetime

import pytest
from dateutil.parser import parse as date_parse
from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder
from django.utils.timezone import now as tz_now
from freezegun import freeze_time

from zapier.models import ZapierToken


def jsonify(data: dict) -> dict:
    """Convert a python dict into a JSON-compatible dict."""
    return json.loads(json.dumps(data, cls=DjangoJSONEncoder))


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
        add_scope: str,
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

    @pytest.mark.parametrize(
        "recent_requests,scope,result",
        [
            ({"foo": "2021-10-14T19:32:20"}, "foo", date_parse("2021-10-14T19:32:20")),
            ({"foo": "2021-10-14T19:32:20"}, "*", date_parse("2021-10-14T19:32:20")),
            ({"bar": "2021-10-14T19:32:20"}, "*", date_parse("2021-10-14T19:32:20")),
            ({"bar": "2021-10-14T19:32:20"}, "foo", None),
            ({}, "foo", None),
        ],
    )
    def test_requet_timestamp(
        self,
        zapier_token: ZapierToken,
        recent_requests: dict,
        scope: str,
        result: datetime,
    ) -> None:
        zapier_token.recent_requests = recent_requests
        assert zapier_token.request_timestamp(scope) == result

    def test_log_request(self, zapier_token: ZapierToken) -> None:
        assert zapier_token.recent_requests == {}
        now = tz_now()
        with freeze_time(now):
            zapier_token.log_request("foo")
        # pre-serialized form is the actual date
        assert zapier_token.recent_requests == {"foo": now}
        zapier_token.refresh_from_db()
        assert zapier_token.recent_requests == jsonify({"foo": now})

    def test_refresh(self, zapier_token: ZapierToken) -> None:
        """Test refresh method updates the api_token."""
        old_token = zapier_token.api_token
        zapier_token.refresh()
        assert zapier_token.api_token != old_token
        zapier_token.refresh_from_db()
        assert zapier_token.api_token != old_token

    def test_reset(self, zapier_token: ZapierToken) -> None:
        """Test reset method clears out recent_requests."""
        zapier_token.log_request("foo")
        assert zapier_token.recent_requests
        zapier_token.reset()
        assert not zapier_token.recent_requests
        zapier_token.refresh_from_db()
        assert not zapier_token.recent_requests

    def test_revoke(self, zapier_token: ZapierToken) -> None:
        """Test revoke method removes all scopes."""
        old_scopes = zapier_token.api_scopes
        assert old_scopes
        zapier_token.revoke()
        assert zapier_token.api_scopes == []
        zapier_token.refresh_from_db()
        assert zapier_token.api_scopes == []
