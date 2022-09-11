# region: private functions for subscribe, unsubscribe, list actions
import logging

import requests
from django.conf import settings as django_settings
from django.utils.timezone import now as tz_now

from zapier.triggers.models import TriggerEvent, TriggerSubscription

logger = logging.getLogger(__name__)


def subscribe(
    user: django_settings.AUTH_USER_MODEL, trigger: str, target_url: str
) -> TriggerSubscription:
    """Create a new REST Hook subscription."""
    # when a zap is disabled the subscription is unsubscribed - in this
    # instance we have an inactive subscription, so we update the target
    # url (it will be different) and reset the timestamps.
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
    subscription.unsubscribe()


def push(subscription: TriggerSubscription, event_data: dict) -> TriggerEvent:
    """Push data to Zapier."""
    logger.debug("Pushing webhook data:\n%s", event_data)
    started_at = tz_now()
    response = requests.post(subscription.target_url, json=event_data)
    return TriggerEvent.objects.create(
        user=subscription.user,
        trigger=subscription.trigger,
        subscription=subscription,
        started_at=started_at,
        finished_at=tz_now(),
        event_type=TriggerEvent.TriggerEventType.REST_HOOK,
        event_data=event_data,
        status_code=response.status_code,
    )
