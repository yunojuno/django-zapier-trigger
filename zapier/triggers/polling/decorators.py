import logging
from functools import wraps
from typing import Callable, TypeAlias

from django.http import HttpRequest, JsonResponse

from .models import PollingTriggerRequest
from .response import parse_response
from .settings import TRIGGER_REQUEST_LOG

logger = logging.getLogger(__name__)


def zapier_view_request_log(scope: str) -> Callable:
    """
    Log a polling trigger request from Zapier.

    Whether or not to log the request is determined by the setting
    ZAPIER_POLLING_REQUEST_LOG, which can be one of three values: `ALL`,
    `NONE`, `NON_ZERO`. The first two are self-explanatory - the third,
    `NON_ZERO` means only record requests that return at least one item
    of data. This can cut down on logging when the data is relatively
    static. `NON_ZERO` is the default.

    """
    def decorator(view_func):

        @wraps(view_func)
        def decorated_func(request: HttpRequest, *view_args, **view_kwargs) -> JsonResponse:

            response: JsonResponse = view_func(request, *view_args, **view_kwargs)

            if not TRIGGER_REQUEST_LOG:
                logger.debug("Ignoring polling request.")
                return response

            data = parse_response(response)
            if not data and TRIGGER_REQUEST_LOG == "NON_ZERO":
                logger.debug("Ignoring empty polling response.")

            count = len(data) if data else 0
            last_object_id = data[0]["id"] if data else ""
            PollingTriggerRequest.objects.create(
                user=request.user,
                scope=scope,
                data=data,
                count=count,
                last_object_id=last_object_id,
            )
            return response
        return decorated_func
    return decorator
