from __future__ import annotations

import pytest
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.test import RequestFactory
from django.utils.timezone import now as tz_now
from freezegun import freeze_time

from zapier import http as http_headers
from zapier.decorators import polling_trigger
from zapier.models import ZapierToken


@pytest.mark.django_db
class TestZapierTrigger:
    @pytest.mark.parametrize("scope", ["foo"])
    def test_decorator(
        self, scope: str, rf: RequestFactory, zapier_token: ZapierToken
    ) -> None:
        request = rf.get("/", HTTP_X_API_TOKEN=str(zapier_token.api_token))
        request.auth = zapier_token

        @polling_trigger(scope)
        def view(request: HttpRequest) -> HttpResponse:
            return JsonResponse([{"id": "ObjA"}, {"id": "ObjB"}], safe=False)

        # we have to JSON encode the time in order to chop the microseconds
        # off the date - as that happens during JSONField serialization.
        now = tz_now()
        with freeze_time(now):
            resp = view(request)
        assert resp.status_code == 200
        assert resp.headers[http_headers.HEADER_SCOPE] == scope
        assert resp.headers[http_headers.HEADER_TOKEN] == zapier_token.api_token_short
        assert resp.headers[http_headers.HEADER_COUNT] == "2"
        assert resp.headers[http_headers.HEADER_OBJECT_ID] == "ObjA"

    def test_scope_mismatch(
        self, rf: RequestFactory, zapier_token: ZapierToken
    ) -> None:
        request = rf.get("/", HTTP_X_API_TOKEN=str(zapier_token.api_token))
        request.auth = zapier_token
        zapier_token.set_scopes(["bar"])

        @polling_trigger("foo")
        def view(request: HttpRequest) -> HttpResponse:
            return JsonResponse([{"id": 1}], safe=False)

        resp = view(request)
        assert resp.status_code == 403
