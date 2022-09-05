from __future__ import annotations

from uuid import uuid4

from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.db import models, transaction
from django.utils.timezone import now as tz_now
from django.utils.translation import gettext_lazy as _lazy

from zapier.authtoken.exceptions import TokenAuthError


class ZapierUser(AnonymousUser):
    """Subclass of anonymous user to identify Zapier requests."""

class AuthToken(models.Model):
    """Per-user Zapier API token."""

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
    is_active = models.BooleanField(
        default=True, help_text=_lazy("True if the token can be used.")
    )

    def __str__(self) -> str:
        return f"Zapier API key [{self.api_key_short}]"

    @property
    def api_key_short(self) -> str:
        """Return short version of the api_key - like short commit hash."""
        return str(self.api_key).split("-")[0]

    @property
    def auth_response(self) -> dict[str, str]:
        """Return default successful auth response payload."""
        return {
            "full_name": self.user.get_full_name(),
            "token": self.api_key_short,
        }

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
        self.api_key = None
        self.is_active = False
        self.refreshed_at = None
        self.revoked_at = tz_now()
        self.save(update_fields=["api_key", "refreshed_at", "revoked_at", "is_active"])

    @transaction.atomic
    def reset(self) -> None:
        """Refresh the token and delete all previous auth requests."""
        self.api_key = uuid4()
        self.is_active = True
        self.refreshed_at = tz_now()
        self.revoked_at = None
        self.save(update_fields=["api_key", "refreshed_at", "revoked_at", "is_active"])
        self.auth_requests.all().delete()

    def get_most_recent_object(self, scope: str) -> dict | None:
        """Return the most recent object logged."""
        if log := (
            self.requests.filter(scope=scope)
            .exclude(count=0)
            .order_by("timestamp")
            .last()
        ):
            return log.most_recent_object
        return None


class TokenAuthRequest(models.Model):
    """Record auth requests."""

    token = models.ForeignKey(
        AuthToken,
        on_delete=models.CASCADE,
        related_name="auth_requests",
    )
    timestamp = models.DateTimeField(default=tz_now)

    class Meta:
        get_latest_by = "timestamp"
