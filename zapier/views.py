from __future__ import annotations

import logging

from django.http import HttpRequest, HttpResponse

from zapier.decorators import zapier_trigger

logger = logging.getLogger(__name__)


@zapier_trigger("*")
def zapier_token_check(request: HttpRequest) -> HttpResponse:
    """Authenticate Zapier token and return 200 - used to configure triggers."""
    logger.debug("Successful zapier auth check: %s", request.auth)
    return HttpResponse("ok")
