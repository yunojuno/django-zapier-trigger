from __future__ import annotations

import logging

from django.conf import settings
from django.db.models import QuerySet
from django.http import HttpRequest, JsonResponse
from django.views import View
from rest_framework import serializers

from zapier.decorators import zapier_trigger
from zapier.models import ZapierToken
from zapier.types import ObjectId

logger = logging.getLogger(__name__)


@zapier_trigger("*")
def zapier_token_check(request: HttpRequest) -> JsonResponse:
    """Authenticate Zapier token and return 200 - used to configure triggers."""
    logger.debug("Successful zapier auth check: %s", request.auth)
    return JsonResponse({"scopes": request.auth.api_scopes})


class PollingTriggerView(View):

    scope: str = "foo"
    serializer_class: serializers.Serializer | None = None

    def get_queryset(self, user: settings.AUTH_USER_MODEL) -> QuerySet:
        raise NotImplementedError

    def get_serializer_class(self) -> serializers.Serializer:
        if not self.serializer_class:
            raise ValueError("serializer attribute is not set.")
        return self.serializer_class

    def get_last_object_id(self, zapier_token: ZapierToken) -> ObjectId:
        """
        Return the id of the last object fetched for this scope.

        Returns -1 if no recent object was fetched.

        """
        if not self.scope:
            raise ValueError("View scope is not set")
        if last_request := zapier_token.get_request_log(self.scope):
            return last_request.obj_id or -1
        return -1

    def get_data(self, qs: QuerySet) -> list:
        serializer = self.get_serializer_class()
        return list(serializer(qs[:25], many=True).data)

    @zapier_trigger(scope)
    def get(self, request: HttpRequest) -> JsonResponse:
        """Fetch latest data for trigger."""
        id = self.get_last_object_id(request.auth)
        qs = self.get_queryset(request.user).filter(id__gt=id).order_by("-id")
        data = self.get_data(qs)
        return JsonResponse(data, safe=False)
