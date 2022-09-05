from __future__ import annotations

import json
from uuid import UUID

from django.http import HttpRequest, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators import csrf

from zapier.authtoken.decorators import authenticate_zapier_view
from zapier.triggers.hooks.models import RestHookSubscription


@csrf.csrf_exempt
@authenticate_zapier_view
def subscribe(request: HttpRequest, hook: str) -> JsonResponse:
    """Create a new REST Hook subscription."""
    data = json.loads(request.body)
    hook_url = data["hookUrl"]
    # when a zap is disabled the subscription is unsubscribed - in this
    # instance we have an inactive subscription, so we update the target
    # url (it will be different) and reset the timestamps.
    if subscription := RestHookSubscription.objects.filter(
        scope=hook,
        user=request.auth.user,
    ).last():
        subscription.resubscribe(hook_url)
    else:
        subscription = RestHookSubscription.objects.create(
            scope=hook,
            user=request.auth.user,
            target_url=hook_url,
        )
    # response JSON is stored in `bundle.subscribeData`
    return JsonResponse({"id": str(subscription.uuid), "scope": hook}, status=201)


@csrf.csrf_exempt
@authenticate_zapier_view
def unsubscribe(request: HttpRequest, hook: str, subscription_id: UUID) -> JsonResponse:
    """Delete a RestHookSubscription."""
    subscription = get_object_or_404(RestHookSubscription, uuid=subscription_id)
    subscription.unsubscribe()
    return JsonResponse({"id": subscription_id}, status=204)


@csrf.csrf_exempt
@authenticate_zapier_view
def list(request: HttpRequest, hook: str) -> JsonResponse:
    """
    Return sample data (sourced from static template).

    This endpoint is used by Zapier to retrieve a sample item for the
    user to use to configure their trigger.

    The data is read from the /templates/zapier directory, and must be
    named {hook}.json.

    """
    return render(request, f"zapier/{hook}.json", content_type="application/json")
