from __future__ import annotations

import logging
from uuid import uuid4

from django.conf import settings as django_settings
from django.db import IntegrityError, models
from django.utils.timezone import now as tz_now
from django.utils.translation import gettext_lazy as _lazy

logger = logging.getLogger(__name__)


class TriggerSubscriptionError(Exception):
    pass


class TriggerSubscriptionQuerySet(models.QuerySet):
    def active(self) -> TriggerSubscriptionQuerySet:
        """Filter active subscriptions."""
        return self.filter(subscribed_at__isnull=False, unsubscribed_at__isnull=True)


class TriggerSubscriptionManager(models.Manager):
    def subscribe(
        self,
        *,
        user: django_settings.AUTH_USER_MODEL,
        trigger: str,
        zap: str,
        target_url: str,
    ) -> TriggerSubscription:
        """Create a new subscription."""
        try:
            return self.create(
                user=user,
                trigger=trigger,
                zap=zap,
                target_url=target_url,
            )
        except IntegrityError as ex:
            raise TriggerSubscriptionError(
                "Error creating duplicate subscription."
            ) from ex


class TriggerSubscription(models.Model):
    """
    Implementation of REST Hooks to store webhook subscriptions.

    See http://resthooks.org/docs/

    """

    uuid = models.UUIDField(
        default=uuid4,
        help_text=_lazy("Public ID"),
    )
    user = models.ForeignKey(
        django_settings.AUTH_USER_MODEL,
        related_name="zapier_subscriptions",
        on_delete=models.CASCADE,
    )
    trigger = models.CharField(
        max_length=50,
        db_index=True,
        help_text=_lazy("The name of the trigger event to subscribe to."),
    )
    zap = models.CharField(
        max_length=25,
        default="",
        blank=True,
        help_text=_lazy(
            "Zap identifier sourced from `${bundle.meta.zap.id}` "
            "in the form 'subscription:22068168'."
        ),
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

    objects = TriggerSubscriptionManager.from_queryset(TriggerSubscriptionQuerySet)()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "trigger", "zap"], name="unique_user_zap"
            )
        ]

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
            "active": self.is_active,
            "trigger": self.trigger,
            "url": self.target_url,
            "user_id": self.user.pk,
            "uuid": self.uuid,
            "zap": self.zap,
        }

    def unsubscribe(self) -> None:
        self.unsubscribed_at = tz_now()
        self.save(update_fields=["unsubscribed_at"])
