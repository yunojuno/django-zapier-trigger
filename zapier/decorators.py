from typing import Callable

from django.http import HttpRequest, HttpResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt

from .exceptions import AuthenticationError
from .settings import request_authenticator


def zapier_view(view_func) -> Callable:
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
            return HttpResponseForbidden(ex)
    # Requests from Zapier will always be exempt from CSRF
    return csrf_exempt(decorated_func)
