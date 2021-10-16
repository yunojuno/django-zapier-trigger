from __future__ import annotations

from uuid import uuid4

import pytest
from django.http import HttpRequest, HttpResponse
from django.test import Client, RequestFactory
from django.urls import reverse

from zapier.decorators import zapier_trigger
from zapier.models import ZapierToken


@zapier_trigger("foo")
def decorated_view(request: HttpRequest) -> HttpResponse:
    return HttpResponse("ok")


@pytest.mark.django_db
def test_successful_authentication(client: Client, zapier_token: ZapierToken) -> None:
    url = reverse("zapier_token_check")
    resp = client.get(url, HTTP_X_API_TOKEN=str(zapier_token.api_token))
    assert resp.status_code == 200, resp.content


@pytest.mark.django_db
def test_unsuccessful_authentication(client: Client, zapier_token: ZapierToken) -> None:
    url = reverse("zapier_token_check")
    resp = client.get(url, HTTP_X_API_TOKEN=str(uuid4()))
    assert resp.status_code == 403, resp


@pytest.mark.django_db
@pytest.mark.parametrize("scope,status_code", [("foo", 200), ("bar", 403)])
def test_scope_mismatch(
    rf: RequestFactory, zapier_token: ZapierToken, scope, status_code
) -> None:
    zapier_token.set_scopes([scope])
    request = rf.get("/", HTTP_X_API_TOKEN=str(zapier_token.api_token))
    request.auth = zapier_token
    resp = decorated_view(request)
    assert resp.status_code == status_code, resp
