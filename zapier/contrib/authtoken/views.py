import json
import logging

from django.http import HttpRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from zapier.contrib.authtoken.models import AuthToken
from zapier.decorators import JsonResponseUnauthorized

logger = logging.getLogger(__name__)


@csrf_exempt
@require_http_methods(["POST"])
def auth_check(request: HttpRequest) -> JsonResponse:
    """
    Authenticate Zapier request.

    This view returns a JSON response that contains the token user's
    full name, token short value. These values can be used to label the
    connection in Zapier.

    The request is logged.

    """
    data = json.loads(request.body.decode())
    try:
        auth_token = AuthToken.objects.get(
            api_key=data["api_key"], user__email=data["email"]
        )
    except AuthToken.DoesNotExist:
        return JsonResponseUnauthorized({"error": "api_key not found for user."})
    else:
        logger.debug("Successful token check for token: %s", auth_token.api_key_short)
        return JsonResponse(data=auth_token.auth_response, safe=False)
