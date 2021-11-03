from __future__ import annotations

import logging
from typing import Any

from django.conf import settings
from django.db.models import QuerySet
from django.http import HttpRequest, JsonResponse
from django.views import View

from zapier.decorators import polling_trigger
from zapier.models import ZapierToken
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
    serializer_class: Any | None = None

    def get_queryset(self, user: settings.AUTH_USER_MODEL) -> QuerySet:
        raise NotImplementedError

    def get_last_object_id(self, zapier_token: ZapierToken) -> ObjectId:
        """
        Return the id of the last object fetched for this scope.

        Returns -1 if no recent object was fetched.

        """
        if last_request := zapier_token.get_request_log(self.scope):
            return last_request.obj_id or -1
        return -1

    def get_data(self, qs: QuerySet) -> list[dict]:
        """
        Convert QuerySet into list of object dicts.

        By default this assumes that the serializer_class is a DRF
        serializer. If it is not, you should set serializer_class to
        None, and override this method.

        """
        if not self.serializer_class:
            raise NotImplementedError(
                "serializer_class is not set - please override get_data method."
            )
        return list(self.serializer_class(qs[:25], many=True).data)

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
            qs = self.get_queryset(request.user).filter(id__gt=id).order_by("-id")
            data = self.get_data(qs)
            return JsonResponse(data, safe=False)

        return _get(request)
