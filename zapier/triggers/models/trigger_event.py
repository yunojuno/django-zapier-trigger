from __future__ import annotations

from datetime import timedelta

from django.conf import settings as django_settings
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.utils.timezone import now as tz_now
from django.utils.translation import gettext_lazy as _lazy

from .trigger_subscription import TriggerSubscription


class TriggerEventQuerySet(models.QuerySet):
    def webhook_events(self) -> TriggerEventQuerySet:
        return self.filter(event_type=TriggerEvent.TriggerEventType.REST_HOOK)

    def polling_events(self) -> TriggerEventQuerySet:
        return self.filter(event_type=TriggerEvent.TriggerEventType.POLLING)


class TriggerEvent(models.Model):
    """Record each webhook POST."""

    class TriggerEventType(models.TextChoices):
        REST_HOOK = ("REST_HOOK", "Push (webhook)")
        POLLING = ("POLLING", "Pull (polling)")

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
    event_type = models.CharField(
        max_length=10,
        choices=TriggerEventType.choices,
    )
    event_data = models.JSONField(
        blank=True,
        null=True,
        encoder=DjangoJSONEncoder,
        help_text=_lazy("JSON data sent to Zapier."),
    )
    started_at = models.DateTimeField(default=tz_now, blank=True, null=True)
    finished_at = models.DateTimeField(blank=True, null=True)
    status_code = models.IntegerField(
        help_text=_lazy("HTTP status code received from Zapier")
    )

    objects = TriggerEventQuerySet.as_manager()

    def __str__(self) -> str:
        return f"'{self.trigger}' event #{self.id}"

    @property
    def is_complete(self) -> bool:
        return self.started_at and self.finished_at

    @property
    def duration(self) -> timedelta | None:
        if not self.is_complete:
            return None
        return self.finished_at - self.started_at

    @property
    def status(self) -> str:
        if not self.response_payload:
            return "unknown"
        return self.response_payload.get("status", "unknown")

    @property
    def is_webhook(self) -> bool:
        return self.event_type == self.TriggerEventType.REST_HOOK

    @property
    def is_polling(self) -> bool:
        return self.event_type == self.TriggerEventType.POLLING
