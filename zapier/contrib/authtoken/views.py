import logging

from django.http import HttpRequest, JsonResponse

from zapier.decorators import zapier_view

logger = logging.getLogger(__name__)


@zapier_view
def auth_check(request: HttpRequest) -> JsonResponse:
    """
    Authenticate Zapier request.

    This view returns a JSON response that contains the token user's
    full name, token short value. These values can be used to label the
    connection in Zapier.

    The request is logged.

    """
    logger.debug("Successful token check for token: %s", request.auth.api_key_short)
    return JsonResponse(data=request.auth.auth_response, safe=False)
