import logging
from functools import wraps
from typing import Any, Callable

from django.http import HttpRequest, JsonResponse

from .models import PollingTriggerRequest
from .response import parse_response
from .settings import TRIGGER_REQUEST_LOG

logger = logging.getLogger(__name__)


def zapier_view_request_log(trigger: str) -> Callable:
    """
    Log a polling trigger request from Zapier.

    Whether or not to log the request is determined by the setting
    ZAPIER_POLLING_REQUEST_LOG, which can be one of three values: `ALL`,
    `NONE`, `NON_ZERO`. The first two are self-explanatory - the third,
    `NON_ZERO` means only record requests that return at least one item
    of data. This can cut down on logging when the data is relatively
    static. `NON_ZERO` is the default.

    """

    def decorator(
        view_func: Callable[..., JsonResponse]
    ) -> Callable[..., JsonResponse]:
        @wraps(view_func)
        def decorated_func(
            request: HttpRequest, *view_args: Any, **view_kwargs: Any
        ) -> JsonResponse:

            response: JsonResponse = view_func(request, *view_args, **view_kwargs)

            if not TRIGGER_REQUEST_LOG:
                logger.debug("Ignoring polling request.")
                return response

            data = parse_response(response)
            if not data and TRIGGER_REQUEST_LOG == "NON_ZERO":
                logger.debug("Ignoring empty polling response.")

            PollingTriggerRequest.objects.create(
                user=request.auth.user,
                trigger=trigger,
                data=data,
            )
            return response

        return decorated_func

    return decorator
