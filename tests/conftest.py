from __future__ import annotations

import pytest
from django.conf import settings

from zapier.models import AuthToken

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
def zapier_token(user: settings.AUTH_USER_MODEL) -> AuthToken:
    return AuthToken.objects.create(user=user, api_scopes=["*"])
