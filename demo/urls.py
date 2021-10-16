from django.contrib import admin
from django.urls import path
from django.views import debug

from zapier.views import zapier_token_check

admin.autodiscover()

urlpatterns = [
    path("", debug.default_urlconf),
    path("admin/", admin.site.urls),
    path("zapier/auth-check/", zapier_token_check, name="zapier_token_check"),
]
