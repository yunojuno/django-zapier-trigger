from django.contrib import admin
from django.urls import path
from django.views import debug

import zapier.views

admin.autodiscover()

urlpatterns = [
    path("", debug.default_urlconf),
    path("admin/", admin.site.urls),
    path(
        "zapier/auth-check/",
        zapier.views.TriggerAuthCheck.as_view(),
        name="zapier_auth_check",
    ),
]
