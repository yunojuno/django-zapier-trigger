from __future__ import annotations

from django.urls import path

from zapier.hooks.views import list, subscribe, unsubscribe

app_name = "zapier.hooks"

urlpatterns = [
    path("<str:hook>/subscribe/", subscribe, name="subscribe"),
    path("<str:hook>/list/", list, name="list"),
    path(
        "<str:hook>/unsubscribe/<uuid:subscription_id>/",
        unsubscribe,
        name="unsubscribe",
    ),
]
