import importlib
from typing import Callable, Type

from django.conf import settings as django_settings
from django.core.exceptions import ImproperlyConfigured
from rest_framework.authentication import BaseAuthentication

from .types import TriggerViewFunc


def import_from_path(path: str) -> Type | Callable:
    """Import function from string path."""
    module, func_or_klass = path.rsplit(".", 1)
    m = importlib.import_module(module)
    return getattr(m, func_or_klass)


# read in settings that have been overridden in django settings.py
_settings = getattr(django_settings, "ZAPIER_TRIGGERS", {})
_settings.setdefault("AUTHENTICATOR", None)
_settings.setdefault("STRICT_MODE", not django_settings.DEBUG)
_settings.setdefault("HOOK_URL_KEY", "hookUrl")
_settings.setdefault("TRIGGERS", {})

# set to True to reject requests that don't come from Zapier
STRICT_MODE = _settings["STRICT_MODE"]

# the JSON key used to extract the REST Hook url from inbound post ("hookUrl")
HOOK_URL_KEY = _settings["HOOK_URL_KEY"]

# map of trigger_name: get_data_func - all triggers must be configured
TRIGGERS = _settings["TRIGGERS"]


def get_authenticator() -> BaseAuthentication:
    """Return authentication class imported from AUTHENTICATOR setting."""
    if not (path := _settings.get("AUTHENTICATOR")):
        raise ImproperlyConfigured("Missing AUTHENTICATOR.")
    return import_from_path(path)


def get_trigger_data_func(trigger: str) -> TriggerViewFunc:
    """Return view data function configured for the trigger."""
    if not (func_path := _settings.get("TRIGGERS", {}).get(trigger)):
        raise ImproperlyConfigured("Missing trigger view function.")
    return import_from_path(func_path)


def trigger_exists(trigger: str) -> bool:
    """Check that the trigger is configured."""
    return trigger in _settings.get("TRIGGERS", {})
