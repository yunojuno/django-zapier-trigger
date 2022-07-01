from __future__ import annotations

import json
from uuid import uuid4

import pytest
from django.test import Client, RequestFactory
from django.urls import reverse

from zapier.models import PollingTriggerRequest, TokenAuthRequest, ZapierToken

from .views import FirstOrLastNameView, FullNameView, User, UsernameView, UserView


@pytest.mark.django_db
def test_successful_authentication(client: Client, zapier_token: ZapierToken) -> None:
    url = reverse("zapier_token_check")
    resp = client.get(url, HTTP_X_API_TOKEN=str(zapier_token.api_token))
    assert resp.status_code == 200, resp.content
    assert json.loads(resp.content) == zapier_token.auth_response


@pytest.mark.django_db
def test_unsuccessful_authentication(client: Client) -> None:
    url = reverse("zapier_token_check")
    resp = client.get(url, HTTP_X_API_TOKEN=str(uuid4()))
    assert resp.status_code == 403, resp


@pytest.mark.django_db
def test_userview(rf: RequestFactory, zapier_token: ZapierToken) -> None:
    """View that does not explicitly select values list."""
    request = rf.get("/", HTTP_X_API_TOKEN=str(zapier_token.api_token))
    request.auth = zapier_token
    view = UserView.as_view()
    with pytest.raises(ValueError):
        _ = view(request)


@pytest.mark.django_db
def test_usernameview(
    rf: RequestFactory, three_users: list[User], zapier_token: ZapierToken
) -> None:
    request = rf.get("/", HTTP_X_API_TOKEN=str(zapier_token.api_token))
    request.auth = zapier_token
    view = UsernameView.as_view()
    resp = view(request)
    assert resp.status_code == 200
    data = json.loads(resp.content)
    assert data == sorted(
        ({"id": u.id, "username": u.username} for u in three_users),
        key=lambda u: u["username"],
        reverse=True,
    )


@pytest.mark.django_db
def test_fullnameview(
    rf: RequestFactory, three_users: list[User], zapier_token: ZapierToken
) -> None:
    request = rf.get("/", HTTP_X_API_TOKEN=str(zapier_token.api_token))
    request.auth = zapier_token
    view = FullNameView.as_view()
    resp = view(request)
    assert resp.status_code == 200
    data = json.loads(resp.content)
    assert data == sorted(
        ({"id": u.id, "full_name": u.get_full_name()} for u in three_users),
        key=lambda u: u["id"],
        reverse=True,
    )


@pytest.mark.django_db
@pytest.mark.parametrize(
    "first_name,expected",
    [
        ("Fred", "first_name"),
        ("Ginger", "full_name"),
    ],
)
def test_firstorlastnameview(
    rf: RequestFactory,
    three_users: list[User],
    zapier_token: ZapierToken,
    first_name: str,
    expected: str,
) -> None:
    user = zapier_token.user
    user.first_name = first_name
    user.save()
    request = rf.get("/", HTTP_X_API_TOKEN=str(zapier_token.api_token))
    request.auth = zapier_token
    view = FirstOrLastNameView.as_view()
    resp = view(request)
    assert resp.status_code == 200
    data = json.loads(resp.content)
    assert data[0]["id"] == three_users[-1].id
    assert expected in data[0]


@pytest.mark.django_db
def test_end_to_end(client, zapier_token: ZapierToken) -> None:
    url1 = reverse("zapier_token_check")
    url2 = reverse("username_view")
    assert TokenAuthRequest.objects.count() == 0
    assert PollingTriggerRequest.objects.count() == 0

    # token auth check
    resp = client.get(url1, HTTP_X_API_TOKEN=str(zapier_token.api_token))
    assert resp.status_code == 200
    assert TokenAuthRequest.objects.count() == 1
    assert PollingTriggerRequest.objects.count() == 0

    # initial trigger request
    resp = client.get(url2, HTTP_X_API_TOKEN=str(zapier_token.api_token))
    assert resp.status_code == 200
    assert TokenAuthRequest.objects.count() == 1
    assert PollingTriggerRequest.objects.count() == 1
