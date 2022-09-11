from __future__ import annotations

from django.urls import path

from .views import TriggerSubscriptions, auth_check

app_name = "zapier_triggers"


urlpatterns = [
    # GET - the auth check URL
    path("auth/", auth_check),
    # GET - the "list" trigger endpoint (returns sample data)
    path("<str:trigger>/", TriggerSubscriptions.as_view()),
    # POST - the "subscribe" endopint
    path("<str:trigger>/subscriptions/", TriggerSubscriptions.as_view()),
    # DELETE - "unsubscribe" endpoint
    path(
        "<str:trigger>/subscriptions/<uuid:subscription_id>/",
        TriggerSubscriptions.as_view(),
    ),
]
