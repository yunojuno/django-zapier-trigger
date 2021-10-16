from __future__ import annotations

from uuid import uuid4

import pytest
from django.contrib.auth import get_user_model
from django.test import Client, RequestFactory
from django.urls import reverse

from zapier.exceptions import TokenAuthenticationError
from zapier.models import ZapierToken
from zapier.views import ZapierPollingTriggerView


@pytest.mark.django_db
class TestZapierPollingTriggerView:
    @pytest.mark.parametrize("api_token", ["", None, "123", uuid4()])
    def test_authenticate__error(
        self,
        rf: RequestFactory,
        api_token: str,
    ) -> None:
        view = ZapierPollingTriggerView()
        request = rf.get("/", HTTP_X_API_TOKEN=api_token)
        with pytest.raises(TokenAuthenticationError):
            view.authenticate(request)

    def test_authenticate__inactive_user(
        self,
        rf: RequestFactory,
        zapier_token: ZapierToken,
    ) -> None:
        view = ZapierPollingTriggerView()
        request = rf.get("/", HTTP_X_API_TOKEN=zapier_token.api_token)
        zapier_token.user.is_active = False
        zapier_token.user.save()
        with pytest.raises(TokenAuthenticationError):
            view.authenticate(request)

    def test_authenticate__authenticated_user(
        self,
        rf: RequestFactory,
        zapier_token: ZapierToken,
    ) -> None:
        view = ZapierPollingTriggerView()
        request = rf.get("/", HTTP_X_API_TOKEN=zapier_token.api_token)
        request.user = get_user_model().objects.create(username=uuid4())
        zapier_token.user.is_active = False
        zapier_token.user.save()
        with pytest.raises(TokenAuthenticationError):
            view.authenticate(request)

    def test_authenticate(
        self,
        rf: RequestFactory,
        zapier_token: ZapierToken,
    ) -> None:
        view = ZapierPollingTriggerView()
        request = rf.get("/", HTTP_X_API_TOKEN=zapier_token.api_token)
        view.authenticate(request)
        assert request.auth == zapier_token
        assert request.user == zapier_token.user


@pytest.mark.django_db
def test_successful_authentication(client: Client, zapier_token: ZapierToken) -> None:
    url = reverse("zapier_auth_check")
    assert client.get(url, HTTP_X_API_TOKEN=zapier_token.api_token).status_code == 200


@pytest.mark.django_db
def test_unsuccessful_authentication(client: Client, zapier_token: ZapierToken) -> None:
    url = reverse("zapier_auth_check")
    assert client.get(url, HTTP_X_API_TOKEN=uuid4()).status_code == 403
