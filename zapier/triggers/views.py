from __future__ import annotations

import json
import logging
from typing import Callable, TypeAlias
from uuid import UUID

from django.shortcuts import get_object_or_404
from django.utils.timezone import now as tz_now
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from zapier.triggers.models.trigger_event import TriggerEvent

from .models import TriggerSubscription
from .settings import AUTHENTICATION_CLASS, LIST_FUNCS
from .subscription import subscribe, unsubscribe

logger = logging.getLogger(__name__)
# type alias for the "list" view functions
TriggerData: TypeAlias = list[dict]
TriggerViewFunc: TypeAlias = Callable[[Request], TriggerData]


@api_view(["GET"])
@authentication_classes([AUTHENTICATION_CLASS])
@permission_classes([IsAuthenticated])
def auth_check(request: Request) -> Response:
    """Support Zapier auth check."""
    logger.debug("Successful authentication request.")
    return Response(
        {"connectionLabel": request.user.username}, content_type="application/json"
    )


class TriggerView(APIView):
    """
    Base class for Zapier REST hook subscriptions.

    This is a base DRF APIView that maps the POST/DELETE/GET methods to
    the Zapier REST hook trigger functions subscribe, unsubscribe, list.

    The AUTHENTICATION_CLASS is read in from the settings.py, and allows
    client applications to control which authentication is used. This
    supports all the authentication mechanisms available to DRF (Token,
    Basic, Session) and its third party extensions (OAuth2 etc.), which
    map onto the auth models that Zapier itself supports. NB Zapier only
    supports one authentication mechanism per app, so this is a single
    value, not a list.

    """

    authentication_classes = [AUTHENTICATION_CLASS]
    permission_classes = [IsAuthenticated]

    def get_trigger_list_func(self, trigger: str) -> TriggerViewFunc:
        return LIST_FUNCS[trigger]

    def get_trigger_data(self, request: Request, trigger: str) -> TriggerData:
        return self.get_trigger_list_func(trigger)(request)

    def get(self, request: Request, trigger: str) -> Response:
        """
        Fetch trigger data.

        Every trigger must have a func configured that will return data
        as the "list" function. For polling triggers this should be the
        real polling trigger data; for resthook triggers this can be
        some static sample data - it is only used for the Zap UI.

        """
        started_at = tz_now()
        event_data = self.get_trigger_data(request, trigger)
        # we only record if data exists.
        if event_data:
            TriggerEvent.objects.create(
                user=request.user,
                trigger=trigger,
                event_data=event_data,
                http_method="GET",
                started_at=started_at,
                finished_at=tz_now(),
                status_code=200,
            )
        return Response(data=event_data, content_type="application/json")

    def post(self, request: Request, trigger: str) -> Response:
        """Create a new webhook subscription."""
        data = json.loads(request.body.decode())
        hook_url = data["hookUrl"]
        subscription = subscribe(request.user, trigger, target_url=hook_url)
        # response JSON is stored in `bundle.subscribeData`
        return Response({"id": str(subscription.uuid)}, status=201)

    def delete(self, request: Request, trigger: str, subscription_id: UUID) -> Response:
        """Deactivate an existing webhook subscription."""
        subscription = get_object_or_404(TriggerSubscription, uuid=subscription_id)
        unsubscribe(subscription)
        return Response(status=204)
