from django.contrib import admin
from django.urls import path

from zapier.views import TriggerAuthCheck

admin.autodiscover()

urlpatterns = [
    path("zapier/auth-check/", TriggerAuthCheck.as_view(), name="zapier_auth_check")
]
