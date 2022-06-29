from __future__ import annotations

import json
from uuid import uuid4

from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.utils.timezone import now as tz_now
from django.utils.translation import gettext_lazy as _lazy

from zapier.exceptions import JsonResponseError


class ZapierUser(AnonymousUser):
    """Subclass of AnonymousUser used to represent the poller on requests."""


class ZapierToken(models.Model):
    """Per-user Zapier API token."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="zapier_token"
    )
    api_token = models.UUIDField(
        default=uuid4, help_text=_lazy("API token for use in Zapier integration")
    )
    api_scopes = models.JSONField(
        default=list,
        help_text=_lazy("List of strings used to define access permissions."),
        blank=True,
    )
    created_at = models.DateTimeField(default=tz_now)
    last_updated_at = models.DateTimeField()

    def __str__(self) -> str:
        return f"Zapier API token for {self.user}"

    @property
    def api_token_short(self) -> str:
        """Return short version of the api_token - like short commit hash."""
        return str(self.api_token).split("-")[0]

    @property
    def auth_response(self) -> dict[str, str]:
        """Return default successful auth response payload."""
        return {
            "name": self.user.get_full_name(),
            "scopes": ",".join(self.api_scopes),
            "token": self.api_token_short,
        }

    def save(self, *args: object, **kwargs: object) -> None:
        if not self.last_updated_at:
            self.last_updated_at = self.created_at
        else:
            self.last_updated_at = tz_now()
        super().save(*args, **kwargs)

    def has_scope(self, scope: str) -> bool:
        # negative scope means excluded.
        if scope == "*":
            raise ValueError("scope argument cannot be '*'")
        if f"-{scope}" in self.api_scopes:
            return False
        if "*" in self.api_scopes:
            return True
        return scope in self.api_scopes

    def add_scope(self, scope: str) -> None:
        """Add a new scope to the token.api_scopes."""
        self.add_scopes([scope])

    def add_scopes(self, scopes: list[str]) -> None:
        """Add new scopes to the token.api_scopes."""
        self.api_scopes = list(set(self.api_scopes + scopes))
        self.save(update_fields=["api_scopes"])

    def remove_scope(self, scope: str) -> None:
        """Remove a scope to the token.api_scopes."""
        self.remove_scopes([scope])

    def remove_scopes(self, scopes: list[str]) -> None:
        """Remove scopes to the token.api_scopes."""
        self.api_scopes = [s for s in self.api_scopes if s and s not in scopes]
        self.save(update_fields={"api_scopes"})

    def set_scopes(self, scopes: list[str]) -> None:
        """Set api_scopes and save object."""
        self.api_scopes = scopes
        self.save(update_fields=["api_scopes"])

    def refresh(self) -> None:
        """Update the api_token."""
        self.api_token = uuid4()
        self.save(update_fields=["api_token"])

    def revoke(self) -> None:
        """Remove all scopes - renders token obsolete."""
        self.api_scopes = []
        self.save(update_fields=["api_scopes"])

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


class ZapierTokenRequestManager(models.Manager):
    def create(
        self, token: ZapierToken, scope: str, content: str | bytes
    ) -> ZapierTokenRequest:
        try:
            data = json.loads(content)
        except json.decoder.JSONDecodeError as ex:
            raise JsonResponseError("Invalid JSON") from ex
        return super().create(
            token=token,
            scope=scope,
            data=data,
            count=len(data) if data else 0,
        )


class ZapierTokenRequest(models.Model):
    """Log of each request received."""

    token = models.ForeignKey(
        ZapierToken, on_delete=models.CASCADE, related_name="requests"
    )
    scope = models.CharField(max_length=50)
    timestamp = models.DateTimeField(default=tz_now)
    data = models.JSONField(
        default=list,
        blank=True,
        help_text=_lazy("The JSON response sent to Zapier."),
        encoder=DjangoJSONEncoder,
    )
    count = models.IntegerField(
        default=0,
        help_text=_lazy("Denormalised object count, used for filtering"),
    )

    objects: ZapierTokenRequestManager = ZapierTokenRequestManager()

    class Meta:
        get_latest_by = "timestamp"
        ordering = ("timestamp",)

    @property
    def most_recent_object(self) -> dict | None:
        """
        Return the first object in the list.

        The data returned to Zapier must be in reverse chronological
        order, so the most recent object is the first in the array.

        """
        if not self.data:
            return None
        return self.data[0]
