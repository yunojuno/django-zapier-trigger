from __future__ import annotations

import pytest
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.test import RequestFactory
from django.utils.timezone import now as tz_now
from freezegun import freeze_time

from zapier.decorators import zapier_trigger
from zapier.models import RequestLog, ZapierToken, encode_timestamp

from .views import CBV


@pytest.mark.django_db
class TestZapierTrigger:
    @pytest.mark.parametrize("scope", ["*", "foo"])
    def test_decorator(
        self, scope: str, rf: RequestFactory, zapier_token: ZapierToken
    ) -> None:
        request = rf.get("/", HTTP_X_API_TOKEN=str(zapier_token.api_token))
        request.auth = zapier_token

        @zapier_trigger(scope)
        def view(request: HttpRequest) -> HttpResponse:
            return JsonResponse([{"id": "ObjA"}, {"id": "ObjB"}], safe=False)

        # we have to JSON encode the time in order to chop the microseconds
        # off the date - as that happens during JSONField serialization.
        now = tz_now()
        with freeze_time(now):
            resp = view(request)
        assert resp.status_code == 200
        assert resp.headers["X-Api-Scope"] == scope
        assert resp.headers["X-Api-Token"] == zapier_token.api_token_short
        if scope == "*":
            assert "X-Api-Count" not in resp.headers
            assert "X-Api-ObjectId" not in resp.headers
            return
        assert resp.headers["X-Api-Count"] == "2"
        assert resp.headers["X-Api-ObjectId"] == "ObjA"
        zapier_token.refresh_from_db()
        assert zapier_token.get_request_log("foo") == (
            RequestLog(encode_timestamp(now), 2, "ObjA")
        )

    def test_scope_mismatch(
        self, rf: RequestFactory, zapier_token: ZapierToken
    ) -> None:
        request = rf.get("/", HTTP_X_API_TOKEN=str(zapier_token.api_token))
        request.auth = zapier_token
        zapier_token.set_scopes(["bar"])

        @zapier_trigger("foo")
        def view(request: HttpRequest) -> HttpResponse:
            return JsonResponse([{"id": 1}], safe=False)

        resp = view(request)
        assert resp.status_code == 403

    def test_cbv(self, rf: RequestFactory, zapier_token: ZapierToken) -> None:
        request = rf.get("/", HTTP_X_API_TOKEN=str(zapier_token.api_token))
        request.auth = zapier_token
        view = CBV.as_view()
        resp = view(request)
        assert resp.status_code == 200, resp
        assert resp.content == b"{}"

    def test_not_a_view(self) -> None:
        @zapier_trigger("foo")
        def not_a_view(request: int) -> None:
            pass

        with pytest.raises(ValueError):
            _ = not_a_view(1)
