from django.contrib import admin
from django.urls import include, path

admin.autodiscover()

urlpatterns = [
    path(
        "zapier/",
        include("zapier.triggers.urls", namespace="zapier_triggers"),
    ),
]
