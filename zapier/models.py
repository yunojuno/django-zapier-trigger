from __future__ import annotations

import json
from datetime import datetime
from uuid import uuid4

from dateutil.parser import parse as date_parse
from django.conf import settings
from django.contrib.postgres import fields as pg_fields
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.http import JsonResponse
from django.utils.timezone import now as tz_now
from django.utils.translation import gettext_lazy as _lazy

from zapier.exceptions import JsonResponseError, TokenScopeError
from zapier.types import ObjectId


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
    request_log = models.JSONField(
        default=dict,
        blank=True,
        help_text=_lazy(
            "{scope: (timestamp, count, obj_id)} map of the latest API request."
        ),
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
        if scope == "*":
            raise ValueError("scope argument cannot be '*'")
        if f"-{scope}" in self.api_scopes:
            return False
        if "*" in self.api_scopes:
            return True
        return scope in self.api_scopes

    def check_scope(self, scope: str) -> None:
        """Raise TokenScopeError if token does not have the scope requested."""
        if not scope:
            raise ValueError("Scope argument is missing or empty.")
        if scope == "*":
            return
        if self.has_scope(scope):
            return
        raise TokenScopeError("Token does not have required scope.")

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

    def _scope_request(self, scope: str) -> tuple[str, int, ObjectId | None] | None:
        if not scope:
            raise ValueError("Missing scope argument.")
        if scope == "*":
            raise ValueError("Invalid scope argument.")
        if not self.request_log:
            return None
        return self.request_log.get(scope, None)

    def get_latest_id(self, scope: str) -> str | int | None:
        """
        Return the id from the last request made for a given scope.

        The response to a trigger request is a JSON-serializable list of
        objects, each of which must have a unique id.

        """
        if not (request := self._scope_request(scope)):
            return None
        return request[2]

    def get_latest_timestamp(self, scope: str) -> datetime | None:
        """Return the timestamp from the last request made for a given scope."""
        if not (request := self._scope_request(scope)):
            return None
        return date_parse(request[0])

    def log_scope_request(self, scope: str, response: JsonResponse) -> None:
        """
        Log an API request/response.

        This method parses the JSON in the response to work out
        what is being returned, and logs the result.

        """
        try:
            data = json.loads(response.content)
        except json.decoder.JSONDecodeError as ex:
            raise JsonResponseError("Invalid JSON") from ex
        else:
            count = len(data)
        try:
            max_id = data[0]["id"] if count else None
        except (TypeError, KeyError, IndexError):
            raise JsonResponseError(
                "Invalid JSON - response contain a list of objects "
                "each of which must have an 'id' attribute."
            )

        # If the Id hasn't changed, use the previous one
        new_id = max_id or self.get_latest_id(scope)
        self.request_log[scope] = (tz_now(), count, new_id)
        self.save(update_fields=["request_log"])

    def reset(self) -> None:
        """
        Clear out the timestamps from request_log.

        This is useful to force a refresh so the user will get the
        full original feed when they next try. Makes testing a lot
        easier - as otherwise you effectively kill the feed on the
        first request (as no new briefs are really being created
        when you are testing).

        """
        self.request_log = {}
        self.save(update_fields=["request_log"])

    def refresh(self) -> None:
        """Update the api_token."""
        self.api_token = uuid4()
        self.save(update_fields=["api_token"])

    def revoke(self) -> None:
        """Remove all scopes - renders token obsolete."""
        self.api_scopes = []
        self.save(update_fields=["api_scopes"])
