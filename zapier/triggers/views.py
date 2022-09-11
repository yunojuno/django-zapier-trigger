from __future__ import annotations

import json
import logging
from uuid import UUID

from django.shortcuts import get_object_or_404
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response, SimpleTemplateResponse
from rest_framework.views import APIView

from .models import TriggerSubscription
from .settings import AUTHENTICATION_CLASS
from .subscription import subscribe, unsubscribe

logger = logging.getLogger(__name__)


@api_view(["GET"])
@authentication_classes([AUTHENTICATION_CLASS])
@permission_classes([IsAuthenticated])
def auth_check(request: Request) -> Response:
    """Support Zapier auth check."""
    logger.debug("Successful authentication request.")
    return Response({"connectionLabel": request.user.username})


class TriggerSubscriptions(APIView):
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

    def get(self, request: Request, trigger: str) -> Response:
        """Fetch some sample data."""
        return SimpleTemplateResponse(
            template=f"zapier/{trigger}.json", content_type="application/json"
        )

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
