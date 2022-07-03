import logging

from django.http import HttpRequest, JsonResponse

from zapier.decorators import zapier_auth

logger = logging.getLogger(__name__)


@zapier_auth
def auth_check(request: HttpRequest) -> JsonResponse:
    """
    Confirm Zapier request authentication.

    This view returns a JSON response that contains the apiKey so that
    it can used in subsequent Zapier requests as bundle.authData.apiKey
    name and a connectionLabel value that can be used to label
    connections.

    """
    logger.debug("Successful auth check: %s", request.auth.api_key_short)
    return JsonResponse(data=request.auth.auth_response, safe=False)
