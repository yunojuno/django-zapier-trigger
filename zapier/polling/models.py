from __future__ import annotations

import json

from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.utils.timezone import now as tz_now
from django.utils.translation import gettext_lazy as _lazy

from zapier.authtoken.exceptions import JsonResponseError
from zapier.authtoken.models import AuthToken


class PollingTriggerRequestManager(models.Manager):
    def create(
        self, token: AuthToken, scope: str, content: str | bytes
    ) -> PollingTriggerRequest:
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


class PollingTriggerRequest(models.Model):
    """Record polling trigger requests."""

    token = models.ForeignKey(
        AuthToken, on_delete=models.CASCADE, related_name="requests"
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

    objects: PollingTriggerRequestManager = PollingTriggerRequestManager()

    class Meta:
        get_latest_by = "timestamp"

    @property
    def most_recent_object(self) -> dict | None:
        """
        Return the first object in the list.

        The data returned to Zapier must be in reverse chronological
        order, so the most recent object is the first in the array.

        If the data logged was a token check then this returns None,
        as token checks don't return "data" per se.

        """
        if not self.data:
            return None
        return self.data[0]
