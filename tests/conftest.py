from __future__ import annotations

import pytest
from django.conf import settings
from rest_framework.authtoken.models import Token

from .factories import UserFactory


@pytest.fixture
def uf() -> UserFactory:
    return UserFactory


@pytest.fixture
def user(uf) -> settings.AUTH_USER_MODEL:
    return uf.create()


@pytest.fixture
def two_users(uf: UserFactory) -> list[settings.AUTH_USER_MODEL]:
    return uf.create_batch(3)


@pytest.fixture
def three_users(uf: UserFactory) -> list[settings.AUTH_USER_MODEL]:
    return uf.create_batch(3)


@pytest.fixture
def active_token(user: settings.AUTH_USER_MODEL) -> Token:
    return Token.objects.create(user=user)
