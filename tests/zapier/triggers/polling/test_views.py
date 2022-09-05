from __future__ import annotations

import json

import pytest
from django.test import RequestFactory
from django.urls import reverse

from zapier.contrib.authtoken.models import AuthToken
from zapier.triggers.polling.models import PollingTriggerRequest

from .views import FirstOrLastNameView, FullNameView, User, UsernameView


@pytest.mark.django_db
def test_usernameview(
    rf: RequestFactory, three_users: list[User], zapier_token: AuthToken
) -> None:
    request = rf.get("/", HTTP_AUTHORIZATION=f"Bearer {zapier_token.api_key}")
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
    rf: RequestFactory, three_users: list[User], zapier_token: AuthToken
) -> None:
    request = rf.get("/", HTTP_AUTHORIZATION=f"Bearer {zapier_token.api_key}")
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
    zapier_token: AuthToken,
    first_name: str,
    expected: str,
) -> None:
    user = zapier_token.user
    user.first_name = first_name
    user.save()
    request = rf.get("/", HTTP_AUTHORIZATION=f"Bearer {zapier_token.api_key}")
    request.auth = zapier_token
    view = FirstOrLastNameView.as_view()
    resp = view(request)
    assert resp.status_code == 200
    data = json.loads(resp.content)
    assert data[0]["id"] == three_users[-1].id
    assert expected in data[0]


@pytest.mark.django_db
def test_end_to_end(client, zapier_token: AuthToken) -> None:
    url1 = reverse("zapier:auth_check")
    url2 = reverse("username_view")
    assert PollingTriggerRequest.objects.count() == 0

    # token auth check
    resp = client.get(url1, HTTP_AUTHORIZATION=f"Bearer {zapier_token.api_key}")
    assert resp.status_code == 200
    assert PollingTriggerRequest.objects.count() == 0

    # initial trigger request
    resp = client.get(url2, HTTP_AUTHORIZATION=f"Bearer {zapier_token.api_key}")
    assert resp.status_code == 200
    assert PollingTriggerRequest.objects.count() == 1
