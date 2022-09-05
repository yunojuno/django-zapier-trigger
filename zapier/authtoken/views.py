import logging

from django.http import HttpRequest, HttpResponseForbidden, JsonResponse

from .models import TokenAuthRequest

logger = logging.getLogger(__name__)
from .decorators import authenticate_zapier_view


@authenticate_zapier_view
def auth_check(request: HttpRequest) -> JsonResponse:
    """
    Authenticate Zapier request.

    This view returns a JSON response that contains the token user's
    full name, token short value. These values can be used to label the
    connection in Zapier.

    The request is logged.

    """
    logger.debug("Successful token check for token: %s", request.auth.api_key_short)
    TokenAuthRequest.objects.create(token=request.auth)
    return JsonResponse(data=request.auth.auth_response, safe=False)
