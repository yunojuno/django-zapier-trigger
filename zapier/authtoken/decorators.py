from __future__ import annotations

from functools import wraps
from typing import Callable

from django.db import transaction
from django.http import HttpRequest, HttpResponse, HttpResponseForbidden, JsonResponse

from .exceptions import TokenAuthError
from .views import authenticate_request, authorize_request

# from zapier.http import HEADER_COUNT, HEADER_OBJECT_ID, HEADER_SCOPE, HEADER_TOKEN


def authenticate() -> Callable:
    """Authenticate token requests."""

    def decorator(view_func: Callable) -> Callable:
        @wraps(view_func)
        @transaction.atomic
        def inner(
            request: HttpRequest, *view_args: object, **view_kwargs: object
        ) -> HttpResponse:
            try:
                authenticate_request(request)
                return view_func(request, *view_args, **view_kwargs)
            except TokenAuthError as ex:
                return HttpResponseForbidden(ex)

        return inner

    return decorator


def authorize(scope: str) -> Callable:
    """
    Decorate view functions that require ZapierToken authentication.

    If a scope is passed in (anything other than "*") then the
    token.api_scopes is checked. After the inner view function is called
    the request is logged. Returns 403 response if the token is invalid.
    """

    def decorator(view_func: Callable) -> Callable:
        @wraps(view_func)
        @transaction.atomic
        def inner(
            request: HttpRequest, *view_args: object, **view_kwargs: object
        ) -> HttpResponse:
            try:
                authorize_request(request, scope)
                response: JsonResponse = view_func(request, *view_args, **view_kwargs)
            except TokenAuthError as ex:
                return HttpResponseForbidden(ex)
                # log_token_request(request.auth, scope, response)
            return response

        return inner

    return decorator
