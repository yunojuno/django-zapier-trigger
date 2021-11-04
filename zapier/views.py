from __future__ import annotations

import logging
from typing import Any

from django.db.models import QuerySet
from django.db.models.query import ValuesIterable
from django.http import HttpRequest, JsonResponse
from django.views import View

from zapier.decorators import polling_trigger
from zapier.models import ZapierToken
from zapier.settings import DEFAULT_PAGE_SIZE
from zapier.types import ObjectId

logger = logging.getLogger(__name__)


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

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        raise NotImplementedError

    def get_last_object_id(self, zapier_token: ZapierToken) -> ObjectId:
        """
        Return the id of the last object fetched for this scope.

        Returns -1 if no recent object was fetched.

        """
        if last_request := zapier_token.get_request_log(self.scope):
            return last_request.obj_id or -1
        return -1

    def serialize(self, qs: QuerySet) -> list[dict]:
        """
        Convert QuerySet into list of object dicts.

        If the serializer_class is set, this method will use it as if it were
        a DRF serializer. If you are rolling your own, then make sure that it
        supports the DRF calling pattern:

            data = Serializer(queryset, many=True).data

        If the serializer_class is not set it falls back to calling `values`
        on the queryset (which converts each object to a dict). If `values`
        has already been called (in the `get_queryset` method), then we just
        return the list as-is. It is STRONGLY recommended that you set explicit
        fields using `values("foo", "bar")` - serializing an entire object's
        fields

        """
        if self.serializer_class:
            return list(self.serializer_class(qs, many=True).data)
        # the get_queryset method has already called `values(...)` on
        # the data. https://github.com/django/django/blob/main/django/db/models/query.py#L869  # noqa
        if qs._iterable_class == ValuesIterable:
            return list(qs)
        # Warning klaxon: this is very dangerous (serializing entire objects)
        raise ValueError(
            "If you are not using a serializer_class you must call `values` on "
            "the queryset return by `get_queryset`."
        )

    def get(self, request: HttpRequest) -> JsonResponse:
        """
        Return the serialized data for the trigger.

        The polling_trigger decorator is designed for view functions,
        not class methods, and so we use a nested function here to do
        the actual work. It's a HACK, but it works. so :shrug:.

        """
        if not self.scope:
            raise ValueError("View scope is not set")

        @polling_trigger(self.scope)
        def _get(request: HttpRequest) -> JsonResponse:
            id = self.get_last_object_id(request.auth)
            qs = (
                self.get_queryset(request)
                .filter(id__gt=id)
                .order_by("-id")[:DEFAULT_PAGE_SIZE]
            )
            data = self.serialize(qs)
            return JsonResponse(data, safe=False)

        return _get(request)
