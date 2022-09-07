import importlib
from typing import Callable

from django.conf import settings
from django.http import HttpRequest


def import_func(fqn: str) -> Callable:
    module, func = fqn.rsplit(".", 1)
    m = importlib.import_module(module)
    return getattr(m, func)


def get_request_authenticator() -> Callable[[HttpRequest], None]:
    request_authenticator = getattr(
        settings,
        "ZAPIER_REQUEST_AUTHENTICATOR",
        "zapier.contrib.authtoken.auth.authenticate_request",
    )
    if callable(request_authenticator):
        return request_authenticator
    # try and load it from a str (path.to.module.func)
    return import_func(request_authenticator)


# global request authenticator, loaded from settings.py
request_authenticator = get_request_authenticator()
