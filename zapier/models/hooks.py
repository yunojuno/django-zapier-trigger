from __future__ import annotations

from django.conf import settings
from django.db import models
from django.utils.timezone import now as tz_now
from django.utils.translation import gettext_lazy as _lazy

from .tokens import ZapierToken


class RestHookSubscription(models.Model):
    """
    Implementation of REST Hooks to store webhook subscriptions.

    See http://resthooks.org/docs/

    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="%(class)ss", on_delete=models.CASCADE
    )
    token = models.ForeignKey(
        ZapierToken,
        on_delete=models.CASCADE,
        help_text=_lazy("The ZapierToken against which to store the webhook."),
        db_index=True,
    )
    scope = models.CharField(
        max_length=50,
        blank=True,
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
        default=tz_now,
        help_text=_lazy("Timestamp marking when the unsubscribe event occurred."),
    )

    @property
    def is_active(self) -> bool:
        """Return True if the subscription is active."""
        return self.subscribed_at and not self.unsubscribed_at

    @property
    def is_inactive(self) -> bool:
        """Return False if the subscription is active."""
        return self.subscribed_at and self.unsubscribed_at
