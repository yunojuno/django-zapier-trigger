from __future__ import annotations

from django.urls import path

from zapier.views import subscribe, unsubscribe, zapier_token_check

app_name = "zapier"

urlpatterns = [
    path("token-check/", zapier_token_check, name="zapier_token_check"),
    path("hooks/subscribe/", subscribe, name="rest_hook_subscribe"),
    path(
        "hooks/unsubscribe/<uuid:subscription_id>/",
        unsubscribe,
        name="rest_hook_unsubscribe",
    ),
]
