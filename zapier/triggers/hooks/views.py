from __future__ import annotations

import json
from uuid import UUID

from django import views
from django.http import HttpRequest, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_http_methods

from zapier.decorators import zapier_auth
from zapier.triggers.hooks.models import RestHookSubscription


@zapier_auth
@require_http_methods(["POST"])
def subscribe(request: HttpRequest, trigger: str) -> JsonResponse:
    """Create a new REST Hook subscription."""
    data = json.loads(request.body)
    hook_url = data["hookUrl"]
    # when a zap is disabled the subscription is unsubscribed - in this
    # instance we have an inactive subscription, so we update the target
    # url (it will be different) and reset the timestamps.
    if subscription := RestHookSubscription.objects.filter(
        trigger=trigger,
        user=request.auth.user,
    ).last():
        subscription.resubscribe(hook_url)
    else:
        subscription = RestHookSubscription.objects.create(
            trigger=trigger,
            user=request.auth.user,
            target_url=hook_url,
        )
    # response JSON is stored in `bundle.subscribeData`
    return JsonResponse({"id": str(subscription.uuid)}, status=201)


@zapier_auth
@require_http_methods(["DELETE"])
def unsubscribe(
    request: HttpRequest, trigger: str, subscription_id: UUID
) -> JsonResponse:
    """Delete a RestHookSubscription."""
    subscription = get_object_or_404(RestHookSubscription, uuid=subscription_id)
    subscription.unsubscribe()
    return JsonResponse({"id": subscription_id}, status=204)


@zapier_auth
@require_http_methods(["GET"])
def list(request: HttpRequest, trigger: str) -> JsonResponse:
    """
    Return sample data (sourced from static template).

    This endpoint is used by Zapier to retrieve a sample item for the
    user to use to configure their trigger.

    The data is read from the /templates/zapier directory, and must be
    named {trigger}.json.

    """
    return render(request, f"zapier/{trigger}.json", content_type="application/json")


class RestHookView(views.View):
    """Class that wraps the view functions - can be used to override."""

    def post(request: HttpRequest, trigger: str) -> JsonResponse:
        return subscribe(request, trigger)

    def delete(
        request: HttpRequest, trigger: str, subscription_id: UUID
    ) -> JsonResponse:
        return unsubscribe(request, trigger, subscription_id)

    def get(request: HttpRequest, trigger: str) -> JsonResponse:
        return list(request, trigger)
