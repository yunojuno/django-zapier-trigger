from __future__ import annotations

import logging

from django.contrib.auth import get_user_model
from django.http import HttpRequest, JsonResponse

from .exceptions import (
    MissingTokenHeader,
    TokenAuthError,
    TokenScopeError,
    TokenUserError,
    UnknownToken,
)
from .models import AuthToken, ZapierUser

User = get_user_model()
logger = logging.getLogger(__name__)


def extract_bearer_token(request: HttpRequest) -> str:
    """Return token from 'Authorization: Bearer {{token}}' request header."""
    if scheme_token := request.headers.get("Authorization", ""):
        return scheme_token.split(" ", 1)[1]
    return ""


def authenticate_request(request: HttpRequest) -> None:
    """
    Authenticate X-Api-Token request header.

    Sets request.user (ZapierUser) and request.auth (AuthToken) from the
    AuthToken that matches the header.

    Raises TokenAuthenticationError if the token is invalid / missing.

    """
    if not (token := extract_bearer_token(request)):
        raise MissingTokenHeader("Missing Authorization request header.")
    try:
        obj: AuthToken = AuthToken.objects.get(api_token=token)
    except AuthToken.DoesNotExist:
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
    if not isinstance(request.auth, AuthToken):
        raise TokenAuthError("Invalid auth object.")
    if not request.auth.has_scope(scope):
        raise TokenScopeError("Token does not have required scope.")
    return


def auth_check(request: HttpRequest) -> JsonResponse:
    """
    Authenticate Zapier token.

    This view returns a JSON response that contains the token
    user's full name, token short value and a CSV string of
    all the token scopes. These values can be used to label
    the connection in Zapier.

    """
    authenticate_request(request)
    logger.debug("Successful token check for token: %s", request.auth.api_token_short)
    return JsonResponse(data=request.auth.auth_response, safe=False)
