from __future__ import annotations

from typing import Type

from django.conf import settings
from django.forms import ValidationError
from django.http import HttpRequest
from rest_framework import authentication, exceptions

from zapier.models import ZapierToken

# DRF expects a (user, token) which it uses to set request.user and
# request.auth properties. This allows you to use `request.auth.has_scope`
# in the handling view.
UserAuth = tuple[Type[settings.AUTH_USER_MODEL], ZapierToken]


class ApiTokenAuthentication(authentication.BaseAuthentication):
    """Authenticate based on 'X-Api-Token' HTTP header."""

    def authenticate(self, request: HttpRequest) -> UserAuth:
        """Return User matching the 'X-Api-Token' header."""
        if not (token := request.headers.get("x-api-token", "")):
            raise exceptions.AuthenticationFailed("Missing X-Api-Token header.")
        try:
            obj: ZapierToken = ZapierToken.objects.get(api_token=token)
        except ValidationError as ex:
            raise exceptions.AuthenticationFailed("Invalid API token.") from ex
        except ZapierToken.DoesNotExist:
            raise exceptions.AuthenticationFailed("Unknown API token.")
        if not obj.user.is_active:
            raise exceptions.AuthenticationFailed("API token user is disabled.")
        return obj.user, obj
