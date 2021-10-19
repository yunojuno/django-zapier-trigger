from __future__ import annotations

from functools import wraps
from typing import Any, Callable

from django.http import HttpRequest, HttpResponse, HttpResponseForbidden

from zapier.auth import authenticate_request
from zapier.exceptions import TokenAuthError


def zapier_trigger(scope: str) -> Callable:
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
        def inner(request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
            try:
                authenticate_request(request)
                request.auth.check_scope(scope)
            except TokenAuthError as ex:
                return HttpResponseForbidden(ex)
            resp = view_func(request, *args, **kwargs)
            if scope and scope != "*":
                request.auth.log_scope_request(scope, resp)
            return resp

        return inner

    return decorator
