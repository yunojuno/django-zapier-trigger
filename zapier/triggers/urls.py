from __future__ import annotations

from django.urls import path

from .views import TriggerView, auth_check

app_name = "zapier_triggers"


urlpatterns = [
    # GET - the auth check URL
    path("auth/", auth_check, name="auth_check"),
    # GET - the "list" trigger endpoint
    path("<str:trigger>/", TriggerView.as_view(), name="list"),
    # POST - the "subscribe" endopint
    path("<str:trigger>/subscriptions/", TriggerView.as_view(), name="subscribe"),
    # DELETE - "unsubscribe" endpoint
    path(
        "<str:trigger>/subscriptions/<uuid:subscription_id>/",
        TriggerView.as_view(),
        name="unsubscribe",
    ),
]
