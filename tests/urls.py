from django.contrib import admin
from django.urls import include, path

from tests.zapier.triggers.polling.views import (
    FirstOrLastNameView,
    FullNameView,
    UsernameView,
    UserView,
)

admin.autodiscover()

urlpatterns = [
    path(
        "zapier/auth/",
        include("zapier.contrib.authtoken.urls", namespace="zapier_auth"),
    ),
    path(
        "zapier/hooks/", include("zapier.triggers.hooks.urls", namespace="zapier_hooks")
    ),
    path("zapier/tests/user/", UserView.as_view(), name="user_view"),
    path("zapier/tests/username/", UsernameView.as_view(), name="username_view"),
    path("zapier/tests/fullname/", FullNameView.as_view(), name="full_view"),
    path(
        "zapier/tests/firstorlast/",
        FirstOrLastNameView.as_view(),
        name="first_or_last_view",
    ),
]
