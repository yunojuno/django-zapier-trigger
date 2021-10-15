# Zapier trigger endpoints
from __future__ import annotations

from django.http import HttpRequest
from rest_framework.response import Response
from rest_framework.views import APIView

from zapier.authentication import ApiTokenAuthentication


class ZapierPollingTrigger(APIView):
    """Base class for polling triggers."""

    authentication_classes = [ApiTokenAuthentication]
    api_scope = "*"

    def get(self, request: HttpRequest) -> Response:
        """Return 200 OK to confirm that api token is valid."""
        return Response({"ok"})
