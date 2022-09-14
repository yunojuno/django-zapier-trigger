import importlib
from typing import Callable, Type

from django.conf import settings as django_settings
from django.core.exceptions import ImproperlyConfigured
from rest_framework.authentication import BaseAuthentication
from rest_framework.request import Request

from .types import TriggerViewFunc


def default_sample_request_func(request: Request) -> bool:
    """
    Return True if the request looks like a Zapier sample data request.

    See https://github.com/zapier/zapier-platform-cli#bundlemeta

    """
    return request.query_params.get("sample", "").lower() == "true"


# read in settings that have been overridden in django settings.py
_settings = getattr(django_settings, "ZAPIER_TRIGGERS", {})
_settings.setdefault("AUTHENTICATOR", None)
_settings.setdefault("STRICT_MODE", not django_settings.DEBUG)
_settings.setdefault("HOOK_URL_KEY", "hookUrl")
_settings.setdefault("ZAP_ID", "zapId")
_settings.setdefault("TRIGGERS", {})
_settings.setdefault("SAMPLE_REQUEST_FUNC", default_sample_request_func)

# set to True to reject requests that don't come from Zapier
STRICT_MODE = _settings["STRICT_MODE"]

# the JSON key used to extract the REST Hook url from inbound post ("hookUrl")
HOOK_URL_KEY = _settings["HOOK_URL_KEY"]

# the JSON key used to extract the zap id from inbound post ("zapId")
ZAP_ID = _settings["ZAP_ID"]

# map of trigger_name: get_data_func - all triggers must be configured
TRIGGERS = _settings["TRIGGERS"]

# customisable function for checking for sample data requests
SAMPLE_REQUEST_FUNC = _settings["SAMPLE_REQUEST_FUNC"]


def import_from_path(path: str) -> Type | Callable:
    """Import function from string path."""
    module, func_or_klass = path.rsplit(".", 1)
    m = importlib.import_module(module)
    return getattr(m, func_or_klass)


def get_authenticator() -> BaseAuthentication:
    """Return authentication class imported from AUTHENTICATOR setting."""
    if not (path := _settings["AUTHENTICATOR"]):
        raise ImproperlyConfigured("Missing AUTHENTICATOR.")
    return import_from_path(path)


def get_trigger(trigger: str) -> TriggerViewFunc:
    """Return view data function configured for the trigger."""
    try:
        return import_from_path(_settings["TRIGGERS"][trigger])
    except KeyError:
        raise ImproperlyConfigured("Missing trigger view function.")


def trigger_exists(trigger: str) -> bool:
    """Check that the trigger is configured."""
    return trigger in _settings["TRIGGERS"]
