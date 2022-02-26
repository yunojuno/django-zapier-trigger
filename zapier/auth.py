from __future__ import annotations

from django.http import HttpRequest

from zapier.exceptions import MissingTokenHeader, TokenUserError, UnknownToken
from zapier.models import ZapierToken, ZapierUser


def authenticate_request(request: HttpRequest) -> None:
    """
    Authenticate X-Api-Token request header.

    Sets request.user (User) and request.auth (ZapierToken) from the
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
        raise TokenUserError("Request user must be anonymous.")
    request.user = ZapierUser()
    request.auth = obj
