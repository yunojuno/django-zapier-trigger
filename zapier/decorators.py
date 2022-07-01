from __future__ import annotations

from functools import wraps
from typing import Callable

from django.db import transaction
from django.http import HttpRequest, HttpResponse, HttpResponseForbidden, JsonResponse

from zapier.auth import authenticate_request, authorize_request
from zapier.exceptions import TokenAuthError
from zapier.http import HEADER_COUNT, HEADER_OBJECT_ID, HEADER_SCOPE, HEADER_TOKEN
from zapier.models import PollingTriggerRequest, TokenAuthRequest, ZapierToken


def log_token_request(
    token: ZapierToken, scope: str, response: HttpResponse
) -> PollingTriggerRequest:
    """Create new PollingTriggerRequest object from HttpResponse."""
    response.headers[HEADER_TOKEN] = token.api_token_short
    response.headers[HEADER_SCOPE] = scope
    response.headers.setdefault(HEADER_COUNT, "0")
    response.headers.setdefault(HEADER_OBJECT_ID, "")
    log = PollingTriggerRequest.objects.create(
        token=token,
        scope=scope,
        content=response.content,
    )
    if log.data:
        response.headers[HEADER_COUNT] = log.count
        response.headers[HEADER_OBJECT_ID] = log.data[0]["id"]
    return log


def polling_trigger(scope: str) -> Callable:
    """
    Decorate view functions that require ZapierToken authentication.

    If a scope is passed in (anything other than "*") then the
    token.api_scopes is checked.

    After the inner view function is called the request is logged.

    Returns 403 response if the token is invalid.

    """

    def decorator(view_func: Callable) -> Callable:
        @wraps(view_func)
        @transaction.atomic
        def inner(
            request: HttpRequest, *view_args: object, **view_kwargs: object
        ) -> HttpResponse:
            try:
                authenticate_request(request)
                authorize_request(request, scope)
                response: JsonResponse = view_func(request, *view_args, **view_kwargs)
            except TokenAuthError as ex:
                return HttpResponseForbidden(ex)
            if scope == ZapierToken.ZAPIER_TOKEN_CHECK_SCOPE:
                TokenAuthRequest.objects.create(token=request.auth)
            else:
                log_token_request(request.auth, scope, response)
            return response

        return inner

    return decorator
