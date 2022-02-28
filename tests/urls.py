from django.contrib import admin
from django.urls import path

from zapier.views import zapier_token_check

from .views import FirstOrLastNameView, FullNameView, UsernameView, UserView

admin.autodiscover()

urlpatterns = [
    path("zapier/auth-check/", zapier_token_check, name="zapier_token_check"),
    path("zapier/tests/user/", UserView.as_view(), name="user_view"),
    path("zapier/tests/username/", UsernameView.as_view(), name="username_view"),
    path("zapier/tests/fullname/", FullNameView.as_view(), name="full_view"),
    path(
        "zapier/tests/firstorlast/",
        FirstOrLastNameView.as_view(),
        name="first_or_last_view",
    ),
]
