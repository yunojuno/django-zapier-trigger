from __future__ import annotations

from django.urls import path

from zapier.views import ZapierPollingTrigger

app_name = "zapier"

urlpatterns = [
    path(
        "check/",
        ZapierPollingTrigger.as_view(),
        name="auth_check",
    ),
]
