from __future__ import annotations

import random

import pytest
from django.conf import settings
from rest_framework.authtoken.models import Token

from zapier.triggers.models import TriggerSubscription

from .factories import UserFactory


@pytest.fixture
def uf() -> UserFactory:
    return UserFactory


@pytest.fixture
def user(uf) -> settings.AUTH_USER_MODEL:
    return uf.create()


@pytest.fixture
def active_token(user: settings.AUTH_USER_MODEL) -> Token:
    return Token.objects.create(user=user)


@pytest.fixture
def zap() -> str:
    return f"subscription:{random.randint(10000000,19999999)}"  # noqa: S311


@pytest.fixture
def active_subscription(active_token: Token, zap: str) -> TriggerSubscription:
    return TriggerSubscription.objects.subscribe(
        user=active_token.user,
        trigger="foo",
        zap=zap,
        target_url="https://www.google.com",
    )


@pytest.fixture
def inactive_subscription(
    active_subscription: TriggerSubscription,
) -> TriggerSubscription:
    active_subscription.unsubscribe()
    return active_subscription
