from __future__ import annotations

from django.urls import path

from zapier.views import zapier_token_check

app_name = "zapier"

urlpatterns = [
    path("token-check/", zapier_token_check, name="zapier_token_check"),
]
