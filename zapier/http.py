from __future__ import annotations

import json
import logging

import requests
from django.core.serializers.json import DjangoJSONEncoder
from django.utils.timezone import now as tz_now

from .models.hooks import RestHookEvent, RestHookSubscription

logger = logging.getLogger(__name__)

HEADER_TOKEN = "X-Api-Token"  # noqa: S105
HEADER_SCOPE = "X-Api-Scope"
HEADER_COUNT = "X-Api-Count"
HEADER_OBJECT_ID = "X-Api-Object-Id"


def trigger_webhook(subscription: RestHookSubscription, payload: dict) -> RestHookEvent:
    """Fire a new webhook request."""
    logger.debug("Processing webhook event for subcription %i", subscription.id)
    started_at = tz_now()
    response = requests.post(
        subscription.target_url,
        json=json.dumps(payload, cls=DjangoJSONEncoder),
        headers={"Content-Type": "application/json"},
        timeout=10,
    )
    finished_at = tz_now()
    try:
        response_json = response.json()
    except json.JSONDecodeError:
        logger.error("Invalid JSON in response body")
        response_json = None
    return RestHookEvent.objects.create(
        subscription=subscription,
        started_at=started_at,
        finished_at=finished_at,
        request_payload=payload,
        response_payload=response_json,
        status_code=response.status_code,
    )
