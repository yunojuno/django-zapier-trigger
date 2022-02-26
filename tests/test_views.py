from __future__ import annotations

import json
from uuid import uuid4

import pytest
from django.test import Client, RequestFactory
from django.urls import reverse
from django.views import View

from zapier.models import ZapierToken
from zapier.views import zapier_token_check

from .views import (
    FirstOrLastNameView,
    FullNameView,
    ReverseUsernameView,
    User,
    UsernameView,
    UserView,
)


@pytest.mark.django_db
def test_successful_authentication(client: Client, zapier_token: ZapierToken) -> None:
    url = reverse("zapier_token_check")
    resp = client.get(url, HTTP_X_API_TOKEN=str(zapier_token.api_token))
    assert resp.status_code == 200, resp.content
    assert resp.content == b"OK"


@pytest.mark.django_db
def test_unsuccessful_authentication(client: Client, zapier_token: ZapierToken) -> None:
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
def test_usernameview(rf: RequestFactory, zapier_token: ZapierToken) -> None:
    user1 = User.objects.create(username="A")
    request = rf.get("/", HTTP_X_API_TOKEN=str(zapier_token.api_token))
    request.auth = zapier_token
    view = UsernameView.as_view()
    resp = view(request)
    assert resp.status_code == 200
    data = json.loads(resp.content)
    assert data == [{"id": user1.id, "username": user1.username}]


@pytest.mark.django_db
def test_firstnameview(rf: RequestFactory, zapier_token: ZapierToken) -> None:
    user = zapier_token.user
    request = rf.get("/", HTTP_X_API_TOKEN=str(zapier_token.api_token))
    request.auth = zapier_token
    view = FullNameView.as_view()
    resp = view(request)
    assert resp.status_code == 200
    data = json.loads(resp.content)
    assert data == [{"id": user.id, "full_name": user.get_full_name()}]


@pytest.mark.django_db
@pytest.mark.parametrize(
    "first_name,expected",
    [
        ("Fred", "first_name"),
        ("Ginger", "full_name"),
    ],
)
def test_firstorlastnameview(
    rf: RequestFactory, zapier_token: ZapierToken, first_name: str, expected: str
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
    assert data[0]["id"] == user.id
    assert expected in data[0]


@pytest.mark.django_db
@pytest.mark.parametrize(
    "view_class,usernames",
    [
        (UsernameView, ["B", "A"]),
        (ReverseUsernameView, ["A", "B"]),
    ],
)
def test_sort_reverse(
    rf: RequestFactory,
    zapier_token: ZapierToken,
    view_class: View,
    usernames: list[str],
) -> None:
    """Confirm the sorting is reverse username."""
    user1 = User.objects.create(username="A")
    user2 = User.objects.create(username="B")
    request = rf.get("/", HTTP_X_API_TOKEN=str(zapier_token.api_token))
    resp = view_class.as_view()(request)
    assert resp.status_code == 200
    data = json.loads(resp.content)
    assert [u["username"] for u in data] == usernames
