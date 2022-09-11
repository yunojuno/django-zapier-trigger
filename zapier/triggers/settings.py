import importlib

from django.conf import settings
from rest_framework.authentication import BaseAuthentication


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
    if authenticator_class == "":
        return None
    if isinstance(authenticator_class, str):
        module, klass = authenticator_class.rsplit(".", 1)
        m = importlib.import_module(module)
        return getattr(m, klass)
    if issubclass(authenticator_class, BaseAuthentication):
        return authenticator_class
    raise ValueError(
        "authentication_class must be a str or BaseAuthentication subclass."
    )


# Class passed to DRF authentication_classes for all Zapier views - NB
# although DRF supports multiple authentication methods, Zapier does not.
AUTHENTICATION_CLASS = get_authenticator(
    getattr(settings, "ZAPIER_TRIGGER_AUTHENTICATION_CLASS", "")
)
