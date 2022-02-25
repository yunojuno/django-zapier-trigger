from __future__ import annotations

import logging
from typing import Any

from django.db.models import QuerySet
from django.db.models.query import ValuesIterable
from django.http import HttpRequest, HttpResponse, HttpResponseForbidden, JsonResponse
from django.views import View

from zapier.auth import authenticate_request
from zapier.decorators import polling_trigger
from zapier.exceptions import TokenAuthError
from zapier.models import ZapierToken
from zapier.settings import DEFAULT_PAGE_SIZE

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
    return HttpResponse("OK")


def serialize(qs: QuerySet, serializer: Any | None) -> list[dict]:
    """
    Convert QuerySet into list of object dicts.

    If the serializer_class is set, this method will use it as if it
    were a DRF serializer. If you are rolling your own, then make sure
    that it supports the DRF calling pattern:

        data = Serializer(queryset, many=True).data

    If the serializer_class is not set it checks whether the queryset
    has been called with `values`. If so, it can return the list as-is
    (`values` returns a list of dicts). If not, this method will raise a
    ValueError.

    """
    if serializer:
        return list(serializer(qs, many=True).data)
    # the get_queryset method has already called `values(...)` on the data:
    # https://github.com/django/django/blob/main/django/db/models/query.py#L869
    if qs._iterable_class == ValuesIterable:
        return list(qs)
    # Warning klaxon: this is very dangerous (serializing entire objects)
    raise ValueError(
        "If you are not using a serializer_class you must call `values` on "
        "the queryset returned by `get_queryset`."
    )


class PollingTriggerView(View):

    scope: str = "REPLACE_WITH_REAL_SCOPE"
    page_size = DEFAULT_PAGE_SIZE
    serializer_class: Any | None = None

    def get_queryset(self, token: ZapierToken) -> QuerySet:
        """Return the next queryset - must be in reverse chrono order."""
        raise NotImplementedError

    def get_page_size(self, request: HttpRequest) -> int:
        """Override to control page size."""
        return self.page_size

    def get_serializer(self, request: HttpRequest) -> Any:
        """Override this to control serializer selection."""
        return self.serializer_class

    def get(self, request: HttpRequest) -> JsonResponse:
        """
        Return the serialized data for the trigger.

        The polling_trigger decorator is designed for view functions,
        not class methods, and so we use a nested function here to do
        the actual work. It's a HACK, but it works.

        NB the Django method_decorator doesn't work for some reason.

        """

        @polling_trigger(scope=self.scope)
        def _get(request: HttpRequest) -> JsonResponse:
            if not self.scope:
                raise ValueError("View scope is not set")
            serializer = self.get_serializer(request)
            page_size = self.get_page_size(request)
            qs = self.get_queryset(token=request.auth)
            data = serialize(qs[:page_size], serializer)
            return JsonResponse(data, safe=False)

        return _get(request)
