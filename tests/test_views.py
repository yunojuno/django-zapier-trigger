from __future__ import annotations

from uuid import uuid4

import pytest
from django.test import Client
from django.urls import reverse

from zapier.models import ZapierToken


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
