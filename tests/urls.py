from django.contrib import admin
from django.urls import path

from zapier.views import zapier_token_check

admin.autodiscover()

urlpatterns = [
    path("zapier/auth-check/", zapier_token_check, name="zapier_token_check")
]
