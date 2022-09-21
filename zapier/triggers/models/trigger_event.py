from __future__ import annotations

from datetime import timedelta
from uuid import uuid4

from django.conf import settings as django_settings
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.utils.timezone import now as tz_now
from django.utils.translation import gettext_lazy as _lazy

from .trigger_subscription import TriggerSubscription


class TriggerEvent(models.Model):

    uuid = models.UUIDField(
        default=uuid4, help_text=_lazy("Public ID used for tracking purposes.")
    )
    user = models.ForeignKey(
        django_settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="zapier_trigger_events",
    )
    trigger = models.CharField(
        max_length=100, help_text=_lazy("The name of the Zapier trigger.")
    )
    subscription = models.ForeignKey(
        TriggerSubscription,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="trigger_events",
        help_text=_lazy(
            "The subscription to which the event was posted (null for polling events)."
        ),
    )
    http_method = models.CharField(
        max_length=4,
        help_text=_lazy("How the data was sent to Zapier - via GET, or POST."),
    )
    event_data = models.JSONField(
        blank=True,
        null=True,
        encoder=DjangoJSONEncoder,
        help_text=_lazy("JSON data sent to Zapier."),
    )
    object_count = models.IntegerField(
        default=0, help_text=_lazy("The count of objects stored in the event_data.")
    )
    started_at = models.DateTimeField(default=tz_now, blank=True, null=True)
    finished_at = models.DateTimeField(blank=True, null=True)
    status_code = models.IntegerField(
        help_text=_lazy("HTTP status code received from Zapier")
    )

    def __str__(self) -> str:
        return f"'{self.trigger}' event #{self.id}"

    @property
    def duration(self) -> timedelta | None:
        if not self.finished_at:
            return None
        return self.finished_at - self.started_at
