from typing import Any, Callable

from django.http import HttpRequest, HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .exceptions import AuthenticationError
from .settings import request_authenticator


class JsonResponseUnauthorized(JsonResponse):

    status_code = 401

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        kwargs.setdefault("headers", {})
        kwargs["headers"]["WWW-Authenticate"] = "Bearer"
        super().__init__(*args, **kwargs)


def zapier_auth(view_func: Callable[..., HttpResponse]) -> Callable[..., HttpResponse]:
    """
    Authenticate requests from Zapier.

    The actual authentication is delegated to a function that
    is set in the zapier.settings.

    """

    def decorated_func(
        request: HttpRequest, *view_args: object, **view_kwargs: object
    ) -> HttpResponse:
        try:
            request_authenticator(request)
            return view_func(request, *view_args, **view_kwargs)
        except AuthenticationError as ex:
            return JsonResponseUnauthorized({"error": str(ex)})

    # Requests from Zapier will always be exempt from CSRF
    return csrf_exempt(decorated_func)


def zapier_view(view_func: Callable[..., JsonResponse]) -> Callable[..., JsonResponse]:
    """
    Validate that view func has request.auth.

    Zapier requests are authenticated using the @zapier_auth decorator -
    this decorated checks that a view has been authenticated - it also
    serves as a useful marker for zapier view funcs.

    """

    def decorated_func(
        request: HttpRequest, *view_args: object, **view_kwargs: object
    ) -> HttpResponse:
        if not hasattr(request, "auth"):
            return JsonResponseUnauthorized(
                {"error": "Unauthorized request (missing auth)."}
            )
        if not request.user.is_authenticated:
            return JsonResponseUnauthorized(
                {"error": "Unauthorized request (missing user)."}
            )
        return view_func(request, *view_args, **view_kwargs)

    return decorated_func
