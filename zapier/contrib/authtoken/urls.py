from __future__ import annotations

from django.urls import path

from .views import auth_check

app_name = "zapier.contrib.authtoken"

urlpatterns = [
    path("", auth_check, name="auth_check"),
]
