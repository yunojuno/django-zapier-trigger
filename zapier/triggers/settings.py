import importlib
from typing import Callable, Type

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from rest_framework.authentication import BaseAuthentication
from rest_framework.request import Request


def import_from_path(path: str) -> Type | Callable:
    """Import function from string path."""
    module, func_or_klass = path.rsplit(".", 1)
    m = importlib.import_module(module)
    return getattr(m, func_or_klass)


def get_authenticator(
    authenticator_class: str | BaseAuthentication,
) -> BaseAuthentication | None:
    """
    Return authentication class from fully-qualified string or class.

    This function is a util used to parse settings values that may be
    either a str ("path.to.module.AuthenticatorClass"), or an import of
    the class itself. When dealing with settings you have to handle the
    import chain - you can't have an instance of a class that is
    declared in an app that has not yet been initialised when the
    settings.py is loaded, so you have to use a string qualifier
    instead.

    """
    if not authenticator_class:
        raise ImproperlyConfigured("Missing ZAPIER_TRIGGERS_AUTHENTICATION_CLASS.")
    if isinstance(authenticator_class, str):
        return import_from_path(authenticator_class)
    if issubclass(authenticator_class, BaseAuthentication):
        return authenticator_class
    raise ValueError(
        "authentication_class must be a str or BaseAuthentication subclass."
    )


# set to True to reject requests that don't come from Zapier
STRICT_MODE = bool(getattr(settings, "ZAPIER_TRIGGERS_STRICT_MODE", not settings.DEBUG))

# Class passed to DRF authentication_classes for all Zapier views - NB
# although DRF supports multiple authentication methods, Zapier does not.
AUTHENTICATION_CLASS = get_authenticator(
    getattr(settings, "ZAPIER_TRIGGERS_AUTHENTICATION_CLASS", "")
)


# {key: func} dict that maps triggers to a polling view func
LIST_FUNCS: dict[str, Callable[[Request], list[dict]]] = {
    key: import_from_path(value)
    for key, value in getattr(settings, "ZAPIER_TRIGGERS_LIST_FUNCS", {}).items()
}
