from __future__ import annotations

from django.http import HttpRequest

from .exceptions import (
    MissingTokenHeader,
    TokenInactiveError,
    TokenUserError,
    UnknownToken,
)
from .models import AuthToken, zapier_user


def extract_bearer_token(request: HttpRequest) -> AuthToken:
    """Return token from 'Authorization: Bearer {{token}}' request header."""
    if bearer_key := request.headers.get("Authorization", ""):
        if not bearer_key.startswith("Bearer "):
            raise MissingTokenHeader("Authorization header is invalid.")
        api_key = bearer_key[7:]
        try:
            return AuthToken.objects.get(api_key=api_key)
        except AuthToken.DoesNotExist:
            raise UnknownToken("Auth token does not exist.")

    raise MissingTokenHeader("Request is missing Authorization header.")


def authenticate_request(request: HttpRequest) -> None:
    """
    Validate Authorization request header.

    Sets request.user and request.auth (AuthToken) from the AuthToken
    that matches the header.

    Raises TokenAuthenticationError if the token is invalid / missing.

    """
    if hasattr(request, "user") and request.user.is_authenticated:
        raise TokenUserError(
            "This does not look like a Zapier request " "(request is authenticated)."
        )
    auth_token = extract_bearer_token(request)
    if not auth_token.is_active:
        raise TokenInactiveError("Auth token is inactive.")
    if not auth_token.user.is_active:
        raise TokenUserError("Auth token user is inactive.")
    request.auth = auth_token
    request.user = zapier_user
