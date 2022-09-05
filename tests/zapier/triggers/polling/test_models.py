from __future__ import annotations

import pytest
from django.http import HttpResponse, JsonResponse

from zapier.contrib.authtoken.models import AuthToken
from zapier.exceptions import JsonResponseError
from zapier.triggers.polling.models import PollingTriggerRequest


class PollingTriggerRequestModelTests:
    def test_create__unparseable_json(self, active_token: AuthToken) -> None:
        with pytest.raises(JsonResponseError):
            response = HttpResponse("foo")
            PollingTriggerRequest.objects.create(active_token, "foo", response.content)

    @pytest.mark.parametrize(
        "content",
        [
            "ok",
            {"id": 0},
            {"id": "foo"},
        ],
    )
    def test_create__invalid_json(self, content, active_token: AuthToken) -> None:
        # invalid json
        with pytest.raises(JsonResponseError):
            response = JsonResponse(content, safe=False)
            PollingTriggerRequest.objects.create(active_token, "foo", response)
