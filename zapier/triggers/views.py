from __future__ import annotations

import json
import logging
from functools import wraps
from typing import Any
from uuid import UUID

from django.http import HttpResponseNotFound
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

from .models import TriggerEvent, TriggerSubscription
from .permissions import IsZapier
from .response import JsonResponse
from .settings import HOOK_URL_KEY, get_authenticator, get_trigger, trigger_exists
from .subscription import subscribe, unsubscribe
from .types import TriggerData, TriggerViewMethod

logger = logging.getLogger(__name__)

AUTHENTICATOR = get_authenticator()


@api_view(["GET"])
@authentication_classes([AUTHENTICATOR])
@permission_classes([IsAuthenticated, IsZapier])
def auth_check(request: Request) -> Response:
    """Support Zapier auth check."""
    logger.debug("Successful authentication request.")
    return JsonResponse({"connectionLabel": request.user.username}, status=200)


def trigger_method(view_method: TriggerViewMethod) -> TriggerViewMethod:
    """Return 404 if trigger passed to view method does not exist."""

    @wraps(view_method)
    def decorated(
        view: TriggerView, request: Request, trigger: str, *args: Any, **kwargs: Any
    ) -> JsonResponse | HttpResponseNotFound:
        if trigger_exists(trigger):
            return view_method(view, request, trigger, *args, **kwargs)
        return HttpResponseNotFound("Unknown trigger request.")

    return decorated


class TriggerView(APIView):
    """
    Manage Zapier REST Hook subscriptions and route polling requests.

    This is a DRF APIView that maps the POST/DELETE/GET methods to the
    Zapier REST hook trigger functions subscribe, unsubscribe, list.

    The AUTHENTICATION_CLASS is read in from the settings.py, and allows
    client applications to control which authentication is used. This
    supports all the authentication mechanisms available to DRF (Token,
    Basic, Session) and its third party extensions (OAuth2 etc.), which
    map onto the auth models that Zapier itself supports. NB Zapier only
    supports one authentication mechanism per app, so this is a single
    value, not a list.

    The POST/DELETE method create / delete REST Hook subscriptions. The
    GET method calls the function configured in IST_FUNCS which can
    either return real data (for a polling trigger), or static sample
    data for a REST Hook.

    The IsZapier permissions class checks for the "Zapier" user-agent if
    STRICT_MODE is enabled.

    The @check_trigger decorator returns a 404 response if the trigger
    parameter is not configured as a LIST_FUNC key.

    """

    authentication_classes = [AUTHENTICATOR]
    permission_classes = [IsAuthenticated, IsZapier]

    def get_trigger_data(self, request: Request, trigger: str) -> TriggerData:
        """Call the configured trigger view function."""
        return get_trigger(trigger)(request)

    @trigger_method
    def get(self, request: Request, trigger: str) -> JsonResponse:
        """
        Fetch trigger data.

        Every trigger must have a func configured that will return data
        as the "list" function. For polling triggers this should be the
        real polling trigger data; for resthook triggers this can be
        some static sample data - it is only used for the Zap UI.

        """
        logger.debug("Fetching data for '%s' trigger.", trigger)
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
        return JsonResponse(data=event_data, status=200, safe=False)

    @trigger_method
    def post(self, request: Request, trigger: str) -> JsonResponse:
        """Create a new webhook subscription."""
        hook_url = json.loads(request.body.decode()).get(HOOK_URL_KEY)
        subscription = subscribe(request.user, trigger, target_url=hook_url)
        # response JSON is stored in `bundle.subscribeData`
        return JsonResponse({"id": str(subscription.uuid)}, status=201)

    @trigger_method
    def delete(
        self, request: Request, trigger: str, subscription_id: UUID
    ) -> JsonResponse:
        """Deactivate an existing webhook subscription."""
        subscription = get_object_or_404(TriggerSubscription, uuid=subscription_id)
        unsubscribe(subscription)
        return JsonResponse({}, status=204)
