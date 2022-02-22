from __future__ import annotations

import logging
from typing import Any

from django.db.models import QuerySet
from django.db.models.query import ValuesIterable
from django.http import HttpRequest, JsonResponse
from django.views import View

from zapier.decorators import polling_trigger
from zapier.settings import DEFAULT_PAGE_SIZE
from zapier.types import ObjectId

logger = logging.getLogger(__name__)

# marker to ensure that we get all objects if none specified
MIN_OBJECT_ID = -1


@polling_trigger("*")
def zapier_token_check(request: HttpRequest) -> JsonResponse:
    """
    Authenticate Zapier token.

    This view does nothing more than return a 200 - it is used by Zapier
    itself to authenticate the API token that the user has set.

    """
    logger.debug("Successful zapier auth check: %s", request.auth)
    return JsonResponse({"scopes": request.auth.api_scopes})


class PollingTriggerView(View):

    scope: str = ""
    page_size = DEFAULT_PAGE_SIZE
    serializer_class: Any | None = None
    sort_by = "id"

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        raise NotImplementedError

    def get_page_size(self, request: HttpRequest) -> int:
        """Override to control page size."""
        return self.page_size

    def get_serializer(self, request: HttpRequest) -> Any:
        """Override this to control serializer selection."""
        return self.serializer_class

    def get_object_id(self, request: HttpRequest) -> ObjectId | None:
        """
        Return the id of the last object fetched for this scope.

        If the request contains a header 'X-Api-Object-Id' then this
        will be used - this is useful for testing purposes - by setting
        this to -1 on a request you ensure that you will get back the
        full dataset.

        """
        if "X-Api-Object-Id" in request.headers:
            return int(request.headers["X-Api-Object-Id"])
        if last_request := request.auth.get_request_log(self.scope):
            return last_request.obj_id
        return None

    def get(self, request: HttpRequest) -> JsonResponse:
        """
        Return the serialized data for the trigger.

        The polling_trigger decorator is designed for view functions,
        not class methods, and so we use a nested function here to do
        the actual work. It's a HACK, but it works. so :shrug:.

        """
        if not self.scope:
            raise ValueError("View scope is not set")

        serializer = self.get_serializer(request)

        @polling_trigger(self.scope)
        def _get(request: HttpRequest) -> JsonResponse:
            page_size = self.get_page_size(request)
            qs = self.get_queryset(request)
            id = self.get_object_id(request) or MIN_OBJECT_ID
            # filtering and ordering is done in the view to ensure that
            # output is in correct order regardless of get_queryset
            # output - you can override what is _in_ the queryset, but
            # not how it is ordered - this is mandated by Zapier.
            qs = qs.filter(**{f"{self.sort_by}__gt": id})
            qs = qs.order_by(f"-{self.sort_by}")
            data = serialize(qs[:page_size], serializer)
            return JsonResponse(data, safe=False)

        return _get(request)


def serialize(qs: QuerySet, serializer: Any | None) -> list[dict]:
    """
    Convert QuerySet into list of object dicts.

    If the serializer_class is set, this method will use it as if it were
    a DRF serializer. If you are rolling your own, then make sure that it
    supports the DRF calling pattern:

        data = Serializer(queryset, many=True).data

    If the serializer_class is not set it checks whether the queryset
    has been called with `values`. If so, it can return the list as-is
    (`values` returns a list of dicts). If not, this method will raise
    a ValueError.

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
