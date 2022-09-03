from uuid import uuid4

import pytest
from django.contrib.auth import get_user_model
from django.test import RequestFactory

from zapier.auth import authenticate_request, authorize_request
from zapier.exceptions import (
    MissingTokenHeader,
    TokenAuthError,
    TokenScopeError,
    TokenUserError,
    UnknownToken,
)
from zapier.models import AuthToken, ZapierUser


@pytest.mark.django_db
class TestAuthenticateRequest:
    def test_authenticate_request(
        self, rf: RequestFactory, zapier_token: AuthToken
    ) -> None:
        request = rf.get("/", HTTP_AUTHORIZATION=f"Bearer {zapier_token.api_token}")
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
        request = rf.get("/", HTTP_AUTHORIZATION=f"Bearer {zapier_token.api_token}")
        zapier_token.user.is_active = False
        zapier_token.user.save()
        with pytest.raises(TokenUserError):
            authenticate_request(request)

    def test_authenticate_token_user_error(
        self, rf: RequestFactory, zapier_token: AuthToken
    ) -> None:
        request = rf.get("/", HTTP_AUTHORIZATION=f"Bearer {zapier_token.api_token}")
        request.user = get_user_model().objects.create(username=str(uuid4()))
        with pytest.raises(TokenUserError):
            authenticate_request(request)


@pytest.mark.django_db
class TestAuthorizeRequest:
    @pytest.mark.parametrize(
        "scopes,scope",
        [
            (["foo"], "foo"),
            (["foo", "bar"], "bar"),
        ],
    )
    def test_authorize_request(
        self,
        rf: RequestFactory,
        zapier_token: AuthToken,
        scopes: list[str],
        scope: str,
    ) -> None:
        zapier_token.set_scopes(scopes)
        request = rf.get("/", HTTP_AUTHORIZATION=f"Bearer {zapier_token.api_token}")
        request.auth = zapier_token
        authorize_request(request, scope)

    @pytest.mark.parametrize(
        "scopes,scope,error",
        [
            (["foo"], "", ValueError),
            (["foo"], "*", ValueError),
            (["foo"], "bar", TokenScopeError),
        ],
    )
    def test_authorize_request__error(
        self,
        rf: RequestFactory,
        zapier_token: AuthToken,
        scopes: list[str],
        scope: str,
        error: type[Exception] | None,
    ) -> None:
        zapier_token.set_scopes(scopes)
        request = rf.get("/", HTTP_AUTHORIZATION=f"Bearer {zapier_token.api_token}")
        request.auth = zapier_token
        with pytest.raises(error):
            authorize_request(request, scope)

    def test_authorize_request__no_token(
        self, rf: RequestFactory, zapier_token: AuthToken
    ) -> None:
        request = rf.get("/", HTTP_AUTHORIZATION=f"Bearer {zapier_token.api_token}")
        with pytest.raises(TokenAuthError):
            authorize_request(request, scope="foo")

    def test_authorize_request__invalid_auth(
        self, rf: RequestFactory, zapier_token: AuthToken
    ) -> None:
        request = rf.get("/", HTTP_AUTHORIZATION=f"Bearer {zapier_token.api_token}")
        request.auth = ZapierUser()
        with pytest.raises(TokenAuthError):
            authorize_request(request, scope="foo")
