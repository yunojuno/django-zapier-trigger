import logging

from django.conf import settings as django_settings

from zapier.triggers.models import TriggerSubscription

logger = logging.getLogger(__name__)


def subscribe(
    user: django_settings.AUTH_USER_MODEL, trigger: str, target_url: str
) -> TriggerSubscription:
    """Create a new REST Hook subscription."""
    # when a zap is disabled the subscription is unsubscribed - in this
    # instance we have an inactive subscription, so we update the target
    # url (it will be different) and reset the timestamps.
    logger.debug("Creating new subscription for trigger '%s'", trigger)
    if subscription := TriggerSubscription.objects.filter(
        trigger=trigger,
        user=user,
    ).last():
        subscription.resubscribe(target_url)
    else:
        subscription = TriggerSubscription.objects.create(
            trigger=trigger,
            user=user,
            target_url=target_url,
        )
    return subscription


def unsubscribe(subscription: TriggerSubscription) -> None:
    """Delete a RestHookSubscription."""
    logger.debug("Deleting subscription '%s'", subscription.uuid)
    subscription.unsubscribe()
