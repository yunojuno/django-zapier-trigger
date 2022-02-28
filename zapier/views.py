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


class PollingTriggerView(View):

    scope: str = "REPLACE_WITH_REAL_SCOPE"
    page_size = DEFAULT_PAGE_SIZE
    serializer: Any = None

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        self.token: ZapierToken | None = None

    def get_most_recent_object(self) -> dict | None:
        """Return the last JSON object that was returned for this token/scope."""
        if not self.token:
            raise Exception("Missing view token.")
        return self.token.get_most_recent_object(self.scope)

    def get_most_recent_object_id(self) -> str | None:
        """Return the id of the last JSON object that was returned."""
        if last_obj := self.most_recent_object():
            return last_obj["id"]
        return None

    def serialize(self, queryset: QuerySet) -> list[dict]:
        """
        Convert QuerySet into list of object dicts.

        If the serializer_class is set, this method will use it as if it
        were a DRF serializer. If you are rolling your own, then make
        sure that it supports the DRF calling pattern:

            data = Serializer(queryset, many=True).data

        If the serializer_class is not set it checks whether the
        queryset has been called with `values`. If so, it can return the
        list as-is (`values` returns a list of dicts). If not, this
        method will raise a ValueError.

        """
        if serializer := self.get_serializer():
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

    def get_queryset(self) -> QuerySet:
        """Return the next queryset - must be in reverse chrono order."""
        raise NotImplementedError

    def get_page_size(self) -> int:
        """Override to control page size."""
        return self.page_size

    def get_serializer(self) -> Any:
        """Override this to control serializer selection."""
        return self.serializer

    def get(self, request: HttpRequest) -> JsonResponse:
        """
        Return the serialized data for the trigger.

        This method contains a function that is itself decorated - this is a
        HACK used to get the concrete class scope into the decorator.
        Using the method_decorator on the outer get method doesn't work.

        """

        @polling_trigger(self.scope)
        def _get(request: HttpRequest) -> None:
            self.token = request.auth
            data = self.serialize(self.get_queryset())
            return JsonResponse(data[: self.get_page_size()], safe=False)

        return _get(request)
