from __future__ import annotations

from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.utils.timezone import now as tz_now
from django.utils.translation import gettext_lazy as _lazy


class PollingTriggerRequest(models.Model):
    """Record polling trigger requests."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="zapier_trigger_requests",
    )
    scope = models.CharField(max_length=50)
    timestamp = models.DateTimeField(default=tz_now)
    data = models.JSONField(
        default=list,
        blank=True,
        help_text=_lazy("The JSON response sent to Zapier."),
        encoder=DjangoJSONEncoder,
    )
    last_object_id = models.CharField(
        max_length=100,
        default="",
        blank=True,
        help_text=_lazy(
            "The id of the most recent object returned to Zapier ("
            "will be empty if no data was returned in this response)."
        ),
    )
    count = models.IntegerField(
        default=0,
        help_text=_lazy("Denormalised object count, used for filtering"),
    )

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
