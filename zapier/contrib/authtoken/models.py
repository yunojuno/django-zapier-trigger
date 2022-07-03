from __future__ import annotations

from uuid import uuid4

from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.db import models
from django.utils.timezone import now as tz_now
from django.utils.translation import gettext_lazy as _lazy

from .exceptions import TokenAuthError


class ZapierUser(AnonymousUser):
    """Subclass of anonymous user to help identify Zapier requests."""


class AuthToken(models.Model):
    """Model used to support API Key authentication for Zapier apps."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="zapier_token"
    )
    api_key = models.UUIDField(
        default=uuid4, help_text=_lazy("API key for use in Zapier integration")
    )
    created_at = models.DateTimeField(
        default=tz_now, help_text=_lazy("When the token was created.")
    )
    refreshed_at = models.DateTimeField(
        default=None,
        blank=True,
        null=True,
        help_text=_lazy("When the token was last refreshed."),
    )
    revoked_at = models.DateTimeField(
        default=None,
        blank=True,
        null=True,
        help_text=_lazy("When the token was last revoked."),
    )

    def __str__(self) -> str:
        return f"Zapier API key [{self.api_key_short}]"

    @property
    def api_key_short(self) -> str:
        """Return short version of the api_key - like short commit hash."""
        return str(self.api_key).split("-")[0]

    @property
    def http_authorization(self) -> str:
        """Return the 'Bearer api_key' header value."""
        return f"Bearer {self.api_key}"

    @property
    def connection_label(self) -> str:
        """Return text to used by Zapier as the connection label."""
        return f"{self.user.username} [{self.api_key_short}]"

    @property
    def auth_response(self) -> dict[str, str]:
        """Return default successful auth response payload."""
        return {
            "connectionLabel": self.connection_label,
            "apiKey": str(self.api_key),
        }

    @property
    def is_active(self) -> bool:
        return not self.revoked_at

    def refresh(self) -> None:
        """Update the api_key."""
        if not self.is_active:
            raise TokenAuthError("Inactive AuthTokens cannot be refreshed.")
        self.api_key = uuid4()
        self.refreshed_at = tz_now()
        self.revoked_at = None
        self.save(update_fields=["api_key", "refreshed_at", "revoked_at"])

    def revoke(self) -> None:
        if not self.is_active:
            raise TokenAuthError("Inactive AuthTokens cannot be revoked.")
        self.revoked_at = tz_now()
        self.save(update_fields=["api_key", "refreshed_at", "revoked_at"])

    def reset(self) -> None:
        """Refresh the token and delete all previous auth requests."""
        self.api_key = uuid4()
        self.refreshed_at = tz_now()
        self.revoked_at = None
        self.save(update_fields=["api_key", "refreshed_at", "revoked_at"])


# instance of ZapierUser used for logging purposes
zapier_user = ZapierUser()
