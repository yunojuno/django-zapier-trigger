from __future__ import annotations

import logging
from typing import Any, TypeAlias

from django.db.models import QuerySet
from django.db.models.query import ValuesIterable
from django.http import HttpRequest, JsonResponse
from django.views import View

from zapier.decorators import zapier_auth

from .decorators import zapier_view_request_log
from .settings import DEFAULT_PAGE_SIZE, get_view_func

# helpful shared mypy type hints
FeedObject: TypeAlias = dict
FeedObjectId: TypeAlias = str | int
FeedData: TypeAlias = list[FeedObject]
# Assumed to be a DRF serializer, but could be anything duck-like.
FeedSerializer: TypeAlias = Any

logger = logging.getLogger(__name__)


class PollingTriggerView(View):

    scope: str = "REPLACE_WITH_TRIGGER_KEY"
    page_size = DEFAULT_PAGE_SIZE
    serializer: FeedSerializer | None = None

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        """Return the next queryset - must be in reverse chrono order."""
        raise NotImplementedError

    def get_page_size(self, request: HttpRequest) -> int:
        """Override to control page size."""
        return self.page_size

    def get_serializer(self, request: HttpRequest) -> FeedSerializer | None:
        """Override to control serializer selection."""
        return self.serializer

    def get_data(
        self, serializer: FeedSerializer, queryset: QuerySet, page_size: int
    ) -> FeedData:
        """
        Convert QuerySet into list of object dicts.

        If the serializer is passed in this method will use it as if it
        were a DRF serializer. If you are rolling your own, then make
        sure that it supports the DRF calling pattern:

            data = Serializer(queryset, many=True).data

        If the serializer is not set it checks whether the queryset has
        been called with `values`. If so, it can return the list as-is
        (`values` returns a list of dicts). If not, this method will
        raise a ValueError.

        """
        queryset = queryset[:page_size]
        if serializer:
            return list(serializer(queryset, many=True).data)

        # the get_queryset method has already called `values(...)` on the data:
        # https://github.com/django/django/blob/main/django/db/models/query.py#L869
        if queryset._iterable_class == ValuesIterable:
            return list(queryset)

        # Warning klaxon: this is very dangerous (serializing entire objects)
        raise ValueError(
            "If you are not using a serializer_class you must call `values` on "
            "the queryset returned by `get_queryset`."
        )

    def get_response(self, data: FeedData) -> JsonResponse:
        """Override to control response attributes."""
        return JsonResponse(data, safe=False)

    def get(self, request: HttpRequest) -> JsonResponse:
        """Return the serialized data for the trigger."""
        @zapier_view_auth  # handles authentication
        @zapier_view_request_log(self.scope)  # logs the request
        def _get(request: HttpRequest) -> JsonResponse:
            queryset = self.get_queryset(request)
            serializer = self.get_serializer(request)
            page_size = self.get_page_size(request)
            data = self.get_data(serializer, queryset, page_size)
            return self.get_response(data)

        return _get(request)


@zapier_auth
def polling_trigger_view(request: HttpRequest, scope: str) -> JsonResponse:
    """Call polling trigger view and record the output."""
    view_func = get_view_func(scope)
    return zapier_view_request_log(scope, view_func(request))
