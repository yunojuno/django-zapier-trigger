from __future__ import annotations

from django.http import HttpRequest

from .exceptions import MissingTokenHeader, TokenUserError, UnknownToken
from .models import AuthToken, ZapierUser


def extract_bearer_token(request: HttpRequest) -> AuthToken:
    """Return token from 'Authorization: Bearer {{token}}' request header."""
    if bearer_key := request.headers.get("Authorization", ""):
        if not bearer_key.startswith("Bearer "):
            raise MissingTokenHeader(
                "Authorization header must be in the form: "
                "Authorization: 'Bearer {API_KEY}'"
            )
        api_key = bearer_key.split(" ", 1)[1]
        try:
            return AuthToken.objects.get(api_key=api_key)
        except AuthToken.DoesNotExist:
            raise UnknownToken("No token was found for supplied api_key.")
    raise MissingTokenHeader(
        "Request must include valid Authorization header in the form "
        "Authorization: 'Bearer {API_KEY}'"
    )


def authenticate_request(request: HttpRequest) -> None:
    """
    Authenticate X-Api-Token request header.

    Sets request.user (ZapierUser) and request.auth (AuthToken) from the
    AuthToken that matches the header.

    Raises TokenAuthenticationError if the token is invalid / missing.

    """
    if hasattr(request, "user") and request.user.is_authenticated:
        raise TokenUserError("This does not look like a Zapier request")
    auth_token = extract_bearer_token(request)
    if not auth_token.user.is_active:
        raise TokenUserError("Auth token user is inactive.")
    request.auth = auth_token
    request.user = ZapierUser()
