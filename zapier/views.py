# Zapier trigger endpoints
from __future__ import annotations

import logging
from typing import Any

from django.forms import ValidationError
from django.http import HttpRequest, HttpResponse, HttpResponseForbidden
from django.http.response import HttpResponseBase
from django.views import View

from zapier.exceptions import TokenAuthenticationError
from zapier.models import ZapierToken

logger = logging.getLogger(__name__)


class ZapierPollingTriggerView(View):
    def authenticate(self, request: HttpRequest) -> None:
        """Return User matching the 'X-Api-Token' header."""
        if hasattr(request, "user") and request.user.is_authenticated:
            raise TokenAuthenticationError
        if not (token := request.headers.get("x-api-token", "")):
            raise TokenAuthenticationError("Missing X-Api-Token header.")
        try:
            obj: ZapierToken = ZapierToken.objects.get(api_token=token)
        # raised if the token is not a valid UUID
        except ValidationError as ex:
            raise TokenAuthenticationError("Invalid API token.") from ex
        except ZapierToken.DoesNotExist:
            raise TokenAuthenticationError("Unknown API token.")
        if not obj.user.is_active:
            raise TokenAuthenticationError("API token user is disabled.")
        request.user = obj.user
        request.auth = obj
        return

    def dispatch(
        self, request: HttpRequest, *args: Any, **kwargs: Any
    ) -> HttpResponseBase:
        try:
            self.authenticate(request)
        except TokenAuthenticationError as ex:
            return HttpResponseForbidden(str(ex))
        return super().dispatch(request, *args, **kwargs)


class TriggerAuthCheck(ZapierPollingTriggerView):
    """
    Default trigger validates the token and returns 200.

    This trigger is used by Zapier to validate the API token that a
    user submits when creating their zap.

    """

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        logger.debug("Successful zapier auth check: %s", request.auth)
        return HttpResponse("ok")
