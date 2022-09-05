from __future__ import annotations

import json
from uuid import uuid4

import pytest
from django.test import Client
from django.urls import reverse

from zapier.authtoken.models import AuthToken


@pytest.mark.django_db
def test_successful_authentication(client: Client, zapier_token: AuthToken) -> None:
    url = reverse("zapier_token_check")
    resp = client.get(url, HTTP_AUTHORIZATION=f"Bearer {zapier_token.api_key}")
    assert resp.status_code == 200, resp.content
    assert json.loads(resp.content) == zapier_token.auth_response


@pytest.mark.django_db
def test_unsuccessful_authentication(client: Client) -> None:
    url = reverse("zapier_token_check")
    resp = client.get(url, HTTP_AUTHORIZATION=f"Bearer {uuid4()}")
    assert resp.status_code == 403, resp
