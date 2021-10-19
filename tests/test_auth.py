from uuid import uuid4

import pytest
from django.contrib.auth import get_user_model
from django.test import RequestFactory

from zapier.auth import authenticate_request
from zapier.exceptions import MissingTokenHeader, TokenUserError, UnknownToken
from zapier.models import ZapierToken


@pytest.mark.django_db
class TestAuthenticateRequest:
    def test_authenticate_request(
        self, rf: RequestFactory, zapier_token: ZapierToken
    ) -> None:
        request = rf.get("/", HTTP_X_API_TOKEN=str(zapier_token.api_token))
        authenticate_request(request)
        assert request.auth == zapier_token
        assert request.user == zapier_token.user

    def test_authenticate_missing_token_header(self, rf: RequestFactory) -> None:
        request = rf.get("/")
        with pytest.raises(MissingTokenHeader):
            authenticate_request(request)
        request = rf.get("/", HTTP_X_API_TOKEN="")
        with pytest.raises(MissingTokenHeader):
            authenticate_request(request)

    def test_authenticate_unknown_token(self, rf: RequestFactory) -> None:
        request = rf.get("/", HTTP_X_API_TOKEN=str(uuid4()))
        with pytest.raises(UnknownToken):
            authenticate_request(request)

    def test_authenticate_inactive_user_error(
        self, rf: RequestFactory, zapier_token: ZapierToken
    ) -> None:
        request = rf.get("/", HTTP_X_API_TOKEN=str(zapier_token.api_token))
        zapier_token.user.is_active = False
        zapier_token.user.save()
        with pytest.raises(TokenUserError):
            authenticate_request(request)

    def test_authenticate_token_user_error(
        self, rf: RequestFactory, zapier_token: ZapierToken
    ) -> None:
        request = rf.get("/", HTTP_X_API_TOKEN=str(zapier_token.api_token))
        request.user = get_user_model().objects.create(username=str(uuid4()))
        with pytest.raises(TokenUserError):
            authenticate_request(request)