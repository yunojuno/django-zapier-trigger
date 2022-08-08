from __future__ import annotations

from uuid import uuid4

from django.conf import settings
from django.db import models
from django.utils.timezone import now as tz_now
from django.utils.translation import gettext_lazy as _lazy

from .tokens import ZapierToken


class RestHookSubscriptionQuerySet(models.QuerySet):
    def active(self) -> RestHookSubscriptionQuerySet:
        """Filter active subscriptions."""
        return self.filter(subscribed_at__isnull=False, unsubscribed_at__isnull=True)


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
    token = models.ForeignKey(
        ZapierToken,
        related_name="webhooks",
        help_text=_lazy("The ZapierToken against which to store the webhook."),
        on_delete=models.CASCADE,
    )
    scope = models.CharField(
        max_length=50,
        db_index=True,
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
            "api_token": self.token.api_token,
            "scope": self.scope,
            "url": self.target_url,
            "active": self.is_active,
        }

    def unsubscribe(self) -> None:
        self.unsubscribed_at = tz_now()
        self.save(update_fields=["unsubscribed_at"])
