from uuid import uuid4

import pytest
from django.test import RequestFactory
from rest_framework import exceptions

from zapier.authentication import ApiTokenAuthentication
from zapier.models import ZapierToken


@pytest.fixture
def auth() -> ApiTokenAuthentication:
    return ApiTokenAuthentication()


@pytest.mark.django_db
class TestApiTokenAuthentication:
    @pytest.mark.parametrize("api_token", ["", None, "123", uuid4()])
    def test_authenticate__error(
        self,
        rf: RequestFactory,
        auth: ApiTokenAuthentication,
        api_token: str,
    ) -> None:
        request = rf.get("/", HTTP_X_API_TOKEN=api_token)
        with pytest.raises(exceptions.AuthenticationFailed):
            auth.authenticate(request)

    def test_authenticate__inactive_user(
        self,
        rf: RequestFactory,
        auth: ApiTokenAuthentication,
        zapier_token: ZapierToken,
    ) -> None:
        request = rf.get("/", HTTP_X_API_TOKEN=zapier_token.api_token)
        zapier_token.user.is_active = False
        zapier_token.user.save()
        with pytest.raises(exceptions.AuthenticationFailed):
            auth.authenticate(request)

    def test_authenticate(
        self,
        rf: RequestFactory,
        auth: ApiTokenAuthentication,
        zapier_token: ZapierToken,
    ) -> None:
        request = rf.get("/", HTTP_X_API_TOKEN=zapier_token.api_token)
        assert auth.authenticate(request) == (zapier_token.user, zapier_token)
