from __future__ import annotations

from django.urls import path

from .views import list, subscribe, unsubscribe

app_name = "zapier_hooks"

urlpatterns = [
    path("<str:trigger>/subscribe/", subscribe, name="subscribe"),
    path("<str:trigger>/list/", list, name="list"),
    path(
        "<str:trigger>/unsubscribe/<uuid:subscription_id>/",
        unsubscribe,
        name="unsubscribe",
    ),
]
