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


def zapier_view_auth(
    view_func: Callable[..., HttpResponse]
) -> Callable[..., HttpResponse]:
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
