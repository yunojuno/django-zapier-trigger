from __future__ import annotations

from django.urls import path

from .views import list, subscribe, unsubscribe

app_name = "zapier_hooks"

urlpatterns = [
    path("<str:hook>/subscribe/", subscribe, name="subscribe"),
    path("<str:hook>/list/", list, name="list"),
    path(
        "<str:hook>/unsubscribe/<uuid:subscription_id>/",
        unsubscribe,
        name="unsubscribe",
    ),
]
