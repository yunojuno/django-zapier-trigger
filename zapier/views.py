from __future__ import annotations

import logging
from typing import Any, TypeAlias

from django.db.models import QuerySet
from django.db.models.query import ValuesIterable
from django.http import HttpRequest, HttpResponseForbidden, JsonResponse
from django.views import View

from zapier.auth import authenticate_request
from zapier.decorators import polling_trigger
from zapier.exceptions import TokenAuthError
from zapier.settings import DEFAULT_PAGE_SIZE

# helpful shared mypy type hints
FeedObject: TypeAlias = dict
FeedObjectId: TypeAlias = str | int
FeedData: TypeAlias = list[FeedObject]
# Assumed to be a DRF serializer, but could be anything duck-like.
FeedSerializer: TypeAlias = Any

logger = logging.getLogger(__name__)


def zapier_token_check(request: HttpRequest) -> JsonResponse:
    """
    Authenticate Zapier token.

    This view does nothing more than return a 200 - it is used by Zapier
    itself to authenticate the API token that the user has set.

    """
    try:
        authenticate_request(request)
    except TokenAuthError:
        logger.exception("Invalid Zapier token authentication request")
        return HttpResponseForbidden()
    return JsonResponse(request.auth.auth_response)


class PollingTriggerView(View):

    scope: str = "REPLACE_WITH_REAL_SCOPE"
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

        @polling_trigger(self.scope)
        def _get(request: HttpRequest) -> JsonResponse:
            queryset = self.get_queryset(request)
            serializer = self.get_serializer(request)
            page_size = self.get_page_size(request)
            data = self.get_data(serializer, queryset, page_size)
            resp = self.get_response(data)
            return resp

        return _get(request)
