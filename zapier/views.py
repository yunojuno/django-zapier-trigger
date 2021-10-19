from __future__ import annotations

import logging

from django.http import HttpRequest, JsonResponse

from zapier.decorators import zapier_trigger

logger = logging.getLogger(__name__)


@zapier_trigger("*")
def zapier_token_check(request: HttpRequest) -> JsonResponse:
    """Authenticate Zapier token and return 200 - used to configure triggers."""
    logger.debug("Successful zapier auth check: %s", request.auth)
    return JsonResponse({"scopes": request.auth.api_scopes})
