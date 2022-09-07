from __future__ import annotations

import json
from typing import Any, Callable, TypeAlias

from django.http import HttpRequest, JsonResponse

from zapier.exceptions import JsonResponseError
from zapier.settings import import_func
from zapier.triggers.polling.settings import VIEW_FUNC_MAP

from .models import PollingTriggerRequest

PollingTriggerViewType: TypeAlias = Callable[[HttpRequest, str], JsonResponse]


class PollingTriggerRequestLogger:
    def __init__(self) -> None:
        self.request: HttpRequest | None = None
        self.scope: str | None = None
        self.data: list[dict] = []

    def __enter__(self) -> PollingTriggerRequestLogger:
        return self

    def __exit__(self, *exc_info: Any) -> None:
        if not self.request:
            raise ValueError("Missing request.")
        PollingTriggerRequest.objects.create(
            user=self.request.user,
            scope=self.scope,
            data=self.data,
            count=self.count,
            last_object_id=self.last_object_id,
        )

    @property
    def count(self) -> int:
        return len(self.data) if self.data else 0

    @property
    def last_object_id(self) -> str:
        return self.data[0]["id"] if self.data else ""

    def _get_view_func(self, scope: str) -> PollingTriggerViewType:
        return import_func(VIEW_FUNC_MAP[scope])

    def _parse_response(self, response: JsonResponse) -> list[dict]:
        try:
            return json.loads(response.content)
        except json.decoder.JSONDecodeError as ex:
            raise JsonResponseError("Invalid JSON") from ex

    def run_view(self, request: HttpRequest, scope: str) -> JsonResponse:
        """Run the mapped view function."""
        self.request = request
        self.scope = scope
        response = self._get_view_func(scope)(request, scope)
        self.data = self._parse_response(response)
        return response
