from __future__ import annotations

from django.urls import path

from zapier.views import TriggerAuthCheck

app_name = "zapier"

urlpatterns = [
    path("check/", TriggerAuthCheck.as_view(), name="auth_check"),
]
