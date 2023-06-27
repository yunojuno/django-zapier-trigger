import logging

import requests
from django.utils.timezone import now as tz_now

from .models import TriggerEvent, TriggerSubscription
from .settings import get_setting

logger = logging.getLogger(__name__)

TIMEOUT = get_setting("REQUESTS_TIMEOUT")


def push(subscription: TriggerSubscription, event_data: dict) -> TriggerEvent:
    """Push data to Zapier."""
    logger.debug("Pushing webhook data:\n%s", event_data)
    started_at = tz_now()
    response = requests.post(subscription.target_url, json=event_data, timeout=TIMEOUT)
    finished_at = tz_now()
    return TriggerEvent.objects.create(
        user=subscription.user,
        trigger=subscription.trigger,
        subscription=subscription,
        started_at=started_at,
        finished_at=finished_at,
        http_method="POST",
        event_data=event_data,
        status_code=response.status_code,
    )
