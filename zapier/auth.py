from __future__ import annotations

from django.http import HttpRequest

from zapier.exceptions import (
    MissingTokenHeader,
    TokenAuthError,
    TokenScopeError,
    TokenUserError,
    UnknownToken,
)
from zapier.models import ZapierToken, ZapierUser


def authenticate_request(request: HttpRequest) -> None:
    """
    Authenticate X-Api-Token request header.

    Sets request.user (ZapierUser) and request.auth (ZapierToken) from the
    ZapierToken that matches the header.

    Raises TokenAuthenticationError if the token is invalid / missing.

    """
    if not (token := request.headers.get("x-api-token", "")):
        raise MissingTokenHeader("Missing X-Api-Token header.")
    try:
        obj: ZapierToken = ZapierToken.objects.get(api_token=token)
    except ZapierToken.DoesNotExist:
        raise UnknownToken("Unknown API token.")
    if not obj.user.is_active:
        raise TokenUserError("API token user is disabled.")
    if hasattr(request, "user") and request.user.is_authenticated:
        raise TokenUserError("Invalid request user.")
    request.user = ZapierUser()
    request.auth = obj


def authorize_request(request: HttpRequest, scope: str) -> None:
    """Raise TokenScopeError if token does not have the scope requested."""
    if not scope:
        raise ValueError("Scope argument is missing or empty.")
    if scope == "*":
        raise ValueError("Invalid scope ('*').")
    if not hasattr(request, "auth"):
        raise TokenAuthError("Request is missing zapier token.")
    if not isinstance(request.auth, ZapierToken):
        raise TokenAuthError("Invalid auth object.")
    if not request.auth.has_scope(scope):
        raise TokenScopeError("Token does not have required scope.")
    return
