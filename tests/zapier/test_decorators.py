from unittest import mock

import pytest
from django.http import HttpRequest, HttpResponse
from django.test import RequestFactory

from zapier.decorators import zapier_auth
from zapier.exceptions import AuthenticationError


def mock_view(request: HttpRequest) -> HttpResponse:
    return HttpResponse("OK")


@pytest.mark.parametrize(
    "side_effect,status_code",
    [
        (None, 200),
        (AuthenticationError, 401),
    ],
)
def test_zapier_auth(rf: RequestFactory, side_effect, status_code) -> None:
    request = rf.post("/")
    request_authenticator = mock.Mock(side_effect=side_effect)
    with mock.patch("zapier.decorators.request_authenticator", request_authenticator):
        assert zapier_auth(mock_view)(request).status_code == status_code
