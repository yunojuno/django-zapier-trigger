from __future__ import annotations

import pytest
from dateutil.parser import parse as date_parse
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.test import RequestFactory
from django.utils.timezone import now as tz_now
from freezegun import freeze_time

from tests.conftest import jsonify
from zapier.decorators import zapier_trigger
from zapier.models import ZapierToken


@pytest.mark.django_db
def test_scope_mismatch(rf: RequestFactory, zapier_token: ZapierToken) -> None:
    request = rf.get("/", HTTP_X_API_TOKEN=str(zapier_token.api_token))
    request.auth = zapier_token

    @zapier_trigger("foo")
    def view(request: HttpRequest) -> HttpResponse:
        return JsonResponse([{"id": 1}], safe=False)

    # we have to JSON encode the time in order to chop the microseconds
    # off the date - as that happens during JSONField serialization.
    now = date_parse(jsonify(tz_now()))
    with freeze_time(now):
        resp = view(request)
    assert resp.status_code == 200
    zapier_token.refresh_from_db()
    assert zapier_token.get_last_request("foo") == (now, 1)
