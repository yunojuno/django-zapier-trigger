from __future__ import annotations

import json
from uuid import uuid4

import pytest
from django.test import Client, RequestFactory
from django.urls import reverse

from zapier.models import ZapierToken

from .factories import UserFactory
from .views import UserTriggerView1, UserTriggerView2, UserTriggerView3


@pytest.mark.django_db
def test_successful_authentication(client: Client, zapier_token: ZapierToken) -> None:
    url = reverse("zapier_token_check")
    resp = client.get(url, HTTP_X_API_TOKEN=str(zapier_token.api_token))
    assert resp.status_code == 200, resp.content
    assert json.loads(resp.content) == {"scopes": zapier_token.api_scopes}


@pytest.mark.django_db
def test_unsuccessful_authentication(client: Client, zapier_token: ZapierToken) -> None:
    url = reverse("zapier_token_check")
    resp = client.get(url, HTTP_X_API_TOKEN=str(uuid4()))
    assert resp.status_code == 403, resp


@pytest.mark.django_db
def test_pollingtriggerview_1(rf: RequestFactory, zapier_token: ZapierToken) -> None:
    """View that does not explicitly select values list."""
    request = rf.get("/", HTTP_X_API_TOKEN=str(zapier_token.api_token))
    request.auth = zapier_token
    view = UserTriggerView1.as_view()
    with pytest.raises(ValueError):
        _ = view(request)


@pytest.mark.django_db
def test_pollingtriggerview_2(rf: RequestFactory, zapier_token: ZapierToken) -> None:
    user1 = zapier_token.user
    user2, user3 = UserFactory.create_batch(2)
    request = rf.get("/", HTTP_X_API_TOKEN=str(zapier_token.api_token))
    request.auth = zapier_token
    view = UserTriggerView2.as_view()
    resp = view(request)
    assert resp.status_code == 200
    data = json.loads(resp.content)
    assert len(data) == 3
    # confirm the only contain the values that are required
    assert data[0] == {"id": user3.id, "username": user3.username}
    assert data[1] == {"id": user2.id, "username": user2.username}
    assert data[2] == {"id": user1.id, "username": user1.username}


@pytest.mark.django_db
def test_pollingtriggerview_3(rf: RequestFactory, zapier_token: ZapierToken) -> None:
    user1 = zapier_token.user
    user2, user3 = UserFactory.create_batch(2)
    request = rf.get("/", HTTP_X_API_TOKEN=str(zapier_token.api_token))
    request.auth = zapier_token
    view = UserTriggerView3.as_view()
    resp = view(request)
    assert resp.status_code == 200
    data = json.loads(resp.content)
    assert len(data) == 3
    # confirm the only contain the values that are required
    assert data[0] == {"id": user3.id, "full_name": user3.get_full_name()}
    assert data[1] == {"id": user2.id, "full_name": user2.get_full_name()}
    assert data[2] == {"id": user1.id, "full_name": user1.get_full_name()}
