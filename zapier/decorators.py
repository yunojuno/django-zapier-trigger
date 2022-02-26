from __future__ import annotations

from functools import wraps
from typing import Callable

from django.http import HttpRequest, HttpResponse, HttpResponseForbidden, JsonResponse

from zapier.auth import authenticate_request
from zapier.exceptions import TokenAuthError
from zapier.http import HEADER_COUNT, HEADER_OBJECT_ID, HEADER_SCOPE, HEADER_TOKEN
from zapier.models import ZapierTokenRequest, ZapierUser


def polling_trigger(scope: str) -> Callable:
    """
    Decorate view functions that require ZapierToken authentication.

    If a scope is passed in (anything other than "*") then the token.api_scopes
    is checked.

    After the inner view function is called the request is logged using the
    request.auth.log_request method.

    Returns 403 response if the token is invalid.

    """

    def decorator(view_func: Callable) -> Callable:
        @wraps(view_func)
        def inner(
            request: HttpRequest, *view_args: object, **view_kwargs: object
        ) -> HttpResponse:
            if not scope:
                raise ValueError("Missing scope.")
            if scope == "*":
                raise ValueError('Invalid view scope ("*").')
            try:
                authenticate_request(request)
                request.auth.check_scope(scope)
            except TokenAuthError as ex:
                return HttpResponseForbidden(ex)
            response: JsonResponse = view_func(request, *view_args, **view_kwargs)
            response.headers[HEADER_TOKEN] = request.auth.api_token_short
            response.headers[HEADER_SCOPE] = scope
            response.headers.setdefault(HEADER_COUNT, "0")
            response.headers.setdefault(HEADER_OBJECT_ID, "")
            log = ZapierTokenRequest.objects.create(
                token=request.auth,
                scope=scope,
                content=response.content,
            )
            if log.data:
                response.headers[HEADER_COUNT] = log.count
                response.headers[HEADER_OBJECT_ID] = log.data[0]["id"]
            return response

        return inner

    return decorator
