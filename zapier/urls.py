from __future__ import annotations

from django.urls import path

from zapier.views import subscribe, unsubscribe, zapier_token_check

from .views.hooks import perform_list

app_name = "zapier"

urlpatterns = [
    path("auth/", zapier_token_check, name="zapier_token_check"),
    path("hooks/subscribe/", subscribe, name="rest_hook_subscribe"),
    path(
        "hooks/unsubscribe/<uuid:subscription_id>/",
        unsubscribe,
        name="rest_hook_unsubscribe",
    ),
    path(
        "hooks/perform_list/<uuid:subscription_id>/",
        perform_list,
        name="rest_hook_perform_list",
    ),
]
