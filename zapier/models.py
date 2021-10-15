from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from dateutil.parser import parse
from django.conf import settings
from django.contrib.postgres import fields as pg_fields
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.utils.timezone import now as tz_now
from django.utils.translation import gettext_lazy as _lazy


class ZapierToken(models.Model):
    """Per-user Zapier API token."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="zapier_token"
    )
    api_token = models.UUIDField(
        default=uuid4, help_text=_lazy("API token for use in Zapier integration")
    )
    api_scopes = pg_fields.ArrayField(
        base_field=models.CharField(max_length=50),
        default=list,
        help_text=_lazy("List of strings used to define access permissions."),
        blank=True,
    )
    recent_requests = models.JSONField(
        default=dict,
        blank=True,
        help_text=_lazy("{scope:timestamp} map of the latest API requests received."),
        encoder=DjangoJSONEncoder,
    )
    created_at = models.DateTimeField(default=tz_now)
    last_updated_at = models.DateTimeField()

    def __str__(self) -> str:
        return f"Zapier API token for {self.user}"

    def save(self, *args: object, **kwargs: object) -> None:
        if not self.last_updated_at:
            self.last_updated_at = self.created_at
        else:
            self.last_updated_at = tz_now()
        super().save(*args, **kwargs)

    def has_scope(self, scope: str) -> bool:
        # negative scope means excluded.
        if f"-{scope}" in self.api_scopes:
            return False
        if "*" in self.api_scopes:
            return True
        return scope in self.api_scopes

    def latest_request(self, scope: str = "*") -> datetime | None:
        """
        Return the last request made for a given scope.

        The timestamp is stored as a JSON, so we need to parse
        it out of the str.

        """
        if not scope:
            raise ValueError("Missing scope argument.")
        if not self.recent_requests:
            return None
        if scope == "*":
            timestamp = max(self.recent_requests.values())
        else:
            timestamp = self.recent_requests.get(scope, None)
        if timestamp:
            return parse(timestamp)
        return None

    def log_request(self, scope: str) -> None:
        """Update the recent_requests property."""
        self.recent_requests[scope] = tz_now()
        self.save(update_fields=["recent_requests"])

    def reset(self) -> None:
        """
        Clear out the timestamps from recent_requests.

        This is useful to force a refresh so the user will get the
        full original feed when they next try. Makes testing a lot
        easier - as otherwise you effectively kill the feed on the
        first request (as no new briefs are really being created
        when you are testing).

        """
        self.recent_requests = {}
        self.save(update_fields=["recent_requests"])

    def refresh(self) -> None:
        """Update the api_token."""
        self.api_token = uuid4()
        self.save(update_fields=["api_token"])

    def revoke(self) -> None:
        """Remove all scopes - renders token obsolete."""
        self.api_scopes = []
        self.save(update_fields=["api_scopes"])
