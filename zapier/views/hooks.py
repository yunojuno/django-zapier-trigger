from __future__ import annotations

import json
from uuid import UUID

from django.http import HttpRequest, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators import csrf

from zapier.auth import authenticate_request
from zapier.models.hooks import RestHookSubscription


@csrf.csrf_exempt
def subscribe(request: HttpRequest) -> JsonResponse:
    """Create a new REST Hook subscription."""
    authenticate_request(request)
    data = json.loads(request.body)
    subscription, _ = RestHookSubscription.objects.get_or_create(
        scope=data["hookScope"],
        target_url=data["hookUrl"],
        user=request.auth.user,
        token=request.auth,
    )
    # response JSON is stored in `bundle.subscribeData`
    return JsonResponse(
        {"id": str(subscription.uuid), "scope": subscription.scope}, status=201
    )


@csrf.csrf_exempt
def unsubscribe(request: HttpRequest, subscription_id: UUID) -> JsonResponse:
    """Delete a RestHookSubscription."""
    authenticate_request(request)
    subscription = get_object_or_404(RestHookSubscription, uuid=subscription_id)
    subscription.unsubscribe()
    return JsonResponse({"id": subscription_id}, status=204)


@csrf.csrf_exempt
def perform_list(request: HttpRequest, subscription_id: UUID) -> JsonResponse:
    """
    Return sample data (sourced from static template).

    This endpoint is used by Zapier to retrieve a sample item for the
    user to use to configure their trigger.

    The data is read from the /templates/zapier directory, and must be
    named {scope}.json.

    """
    authenticate_request(request)
    subscription = get_object_or_404(RestHookSubscription, uuid=subscription_id)
    return render(
        request,
        f"zapier/{subscription.scope}.json",
        status=200,
        content_type="application/json",
    )
