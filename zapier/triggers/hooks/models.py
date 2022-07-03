from __future__ import annotations

import json
import logging
from datetime import timedelta
from typing import Any
from uuid import uuid4

import requests
from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.utils.timezone import now as tz_now
from django.utils.translation import gettext_lazy as _lazy

logger = logging.getLogger(__name__)


def to_json(data: dict | list) -> Any:
    """Use DjangoJSONEncoder to encode Python as JSON."""
    return json.loads(json.dumps(data, cls=DjangoJSONEncoder))


class RestHookSubscriptionQuerySet(models.QuerySet):
    def active(self, trigger: str | None = None) -> RestHookSubscriptionQuerySet:
        """Filter active subscriptions."""
        qs = self.filter(subscribed_at__isnull=False, unsubscribed_at__isnull=True)
        if trigger:
            qs.filter(trigger=trigger)
        return qs


class RestHookSubscription(models.Model):
    """
    Implementation of REST Hooks to store webhook subscriptions.

    See http://resthooks.org/docs/

    """

    uuid = models.UUIDField(
        default=uuid4,
        help_text=_lazy("Public ID"),
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="rest_hooks",
        on_delete=models.CASCADE,
    )
    trigger = models.CharField(
        max_length=50,
        db_index=True,
        help_text=_lazy("The name of the trigger event to subscribe to."),
    )
    target_url = models.URLField(
        help_text=_lazy("The webhook URL to which any payload will be POSTed.")
    )
    subscribed_at = models.DateTimeField(
        default=tz_now,
        help_text=_lazy("Timestamp marking when the initial subscribe event occurred."),
    )
    unsubscribed_at = models.DateTimeField(
        default=None,
        null=True,
        blank=True,
        help_text=_lazy("Timestamp marking when the unsubscribe event occurred."),
    )

    objects = RestHookSubscriptionQuerySet.as_manager()

    def __str__(self) -> str:
        return f"Subscription #{self.id} ('{self.trigger}')"

    @property
    def is_active(self) -> bool:
        """Return True if the subscription is active."""
        return self.subscribed_at and not self.unsubscribed_at

    @property
    def is_inactive(self) -> bool:
        """Return False if the subscription is active."""
        return self.subscribed_at and self.unsubscribed_at

    def serialize(self) -> dict:
        """Serialize object as a JSON-serializable dict."""
        return {
            "uuid": self.uuid,
            "user_id": self.user.pk,
            "trigger": self.trigger,
            "url": self.target_url,
            "active": self.is_active,
        }

    def unsubscribe(self) -> None:
        self.target_url = ""
        self.unsubscribed_at = tz_now()
        self.save(update_fields=["target_url", "unsubscribed_at"])

    def resubscribe(self, target_url: str) -> None:
        self.target_url = target_url
        self.subscribed_at = tz_now()
        self.unsubscribed_at = None
        self.save(update_fields=["target_url", "subscribed_at", "unsubscribed_at"])

    def push(self, event_data: dict) -> RestHookEvent:
        """Push data to Zapier."""
        event = RestHookEvent(
            subscription=self,
            started_at=tz_now(),
            request_payload=event_data,
        )
        logger.debug("Pushing webhook data:\n%s", event_data)
        response = requests.post(self.target_url, json=to_json(event_data))
        response.raise_for_status()
        event.response_payload = response.json()
        event.finished_at = tz_now()
        event.status_code = response.status_code
        event.save()
        return event


class RestHookEvent(models.Model):
    """Record each webhook POST."""

    subscription = models.ForeignKey(
        RestHookSubscription,
        on_delete=models.CASCADE,
        help_text=_lazy("The subscription to which the event was posted."),
    )
    started_at = models.DateTimeField(default=tz_now, blank=True, null=True)
    finished_at = models.DateTimeField(blank=True, null=True)
    request_payload = models.JSONField(blank=True, null=True, encoder=DjangoJSONEncoder)
    response_payload = models.JSONField(
        blank=True, null=True, encoder=DjangoJSONEncoder
    )
    status_code = models.IntegerField()

    def __str__(self) -> str:
        return f"'{self.subscription.trigger}' event #{self.id}"

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
