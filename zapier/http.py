from __future__ import annotations

import json
import logging
from typing import Any, Callable

import requests
from django.core.serializers.json import DjangoJSONEncoder
from django.utils.timezone import now as tz_now
from requests.models import Response

from .models.hooks import RestHookEvent, RestHookSubscription

logger = logging.getLogger(__name__)

HEADER_TOKEN = "X-Api-Token"  # noqa: S105
HEADER_SCOPE = "X-Api-Scope"
HEADER_COUNT = "X-Api-Count"
HEADER_OBJECT_ID = "X-Api-Object-Id"


def trigger_webhook(subscription: RestHookSubscription, payload: dict) -> None:
    """Fire a new webhook request."""
    logger.debug("Processing webhook event for subcription %i", subscription.id)
    response_logger = response_logger_factory(subscription)
    requests.post(
        subscription.target_url,
        json=json.dumps(payload, cls=DjangoJSONEncoder),
        headers={"Content-Type": "application/json"},
        timeout=10,
        hooks={"response": response_logger},
    )


def response_logger_factory(  # noqa: C901 'response_logger_factory' is too complex (9)
    subscription: RestHookSubscription,
) -> Callable:
    # freeze the start timer at the point at which the request is made
    started_at = tz_now()

    def log_response(response: Response, *args: Any, **kwargs: Any) -> None:
        # stop the time at the point at which the response is available
        finished_at = tz_now()
        try:
            response_json = response.json()
        except json.JSONDecodeError:
            logger.error("Invalid JSON in response body")
            response_json = None
        try:
            request_payload = None
            if body := response.request.body:
                # we have to double load to get from bytes to str to dict
                request_payload = json.loads(json.loads(body))
        except Exception:  # noqa: B902
            logger.exception("Error loading request JSON")
        try:
            RestHookEvent.objects.create(
                subscription=subscription,
                started_at=started_at,
                finished_at=finished_at,
                request_payload=request_payload,
                response_payload=response_json,
                status_code=response.status_code,
            )
        except Exception:  # noqa: B902
            logger.exception("Error logging response.")

    return log_response
