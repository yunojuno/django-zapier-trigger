from uuid import uuid4

import pytest
from django.contrib.auth import get_user_model
from django.test import RequestFactory

from zapier.authtoken.decorators import authenticate_request
from zapier.authtoken.exceptions import MissingTokenHeader, TokenUserError, UnknownToken
from zapier.authtoken.models import AuthToken


@pytest.mark.django_db
class TestAuthenticateRequest:
    def test_authenticate_request(
        self, rf: RequestFactory, zapier_token: AuthToken
    ) -> None:
        request = rf.get("/", HTTP_AUTHORIZATION=f"Bearer {zapier_token.api_key}")
        authenticate_request(request)
        assert request.auth == zapier_token
        assert request.user.is_anonymous

    def test_authenticate_missing_token_header(self, rf: RequestFactory) -> None:
        request = rf.get("/")
        with pytest.raises(MissingTokenHeader):
            authenticate_request(request)
        request = rf.get("/", HTTP_AUTHORIZATION="")
        with pytest.raises(MissingTokenHeader):
            authenticate_request(request)

    def test_authenticate_unknown_token(self, rf: RequestFactory) -> None:
        request = rf.get("/", HTTP_AUTHORIZATION=f"Bearer {uuid4()}")
        with pytest.raises(UnknownToken):
            authenticate_request(request)

    def test_authenticate_inactive_user_error(
        self, rf: RequestFactory, zapier_token: AuthToken
    ) -> None:
        request = rf.get("/", HTTP_AUTHORIZATION=f"Bearer {zapier_token.api_key}")
        zapier_token.user.is_active = False
        zapier_token.user.save()
        with pytest.raises(TokenUserError):
            authenticate_request(request)

    def test_authenticate_token_user_error(
        self, rf: RequestFactory, zapier_token: AuthToken
    ) -> None:
        request = rf.get("/", HTTP_AUTHORIZATION=f"Bearer {zapier_token.api_key}")
        request.user = get_user_model().objects.create(username=str(uuid4()))
        with pytest.raises(TokenUserError):
            authenticate_request(request)
