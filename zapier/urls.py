from __future__ import annotations

from django.urls import path

from zapier.views import subscribe, unsubscribe, zapier_token_check

from .views.hooks import list

app_name = "zapier"

urlpatterns = [
    path("auth/", zapier_token_check, name="zapier_token_check"),
    path("hooks/<str:hook>/subscribe/", subscribe, name="rest_hook_subscribe"),
    path(
        "hooks/<str:hook>/unsubscribe/<uuid:subscription_id>/",
        unsubscribe,
        name="rest_hook_unsubscribe",
    ),
    path(
        "hooks/<str:hook>/list/",
        list,
        name="rest_hook_list",
    ),
]
