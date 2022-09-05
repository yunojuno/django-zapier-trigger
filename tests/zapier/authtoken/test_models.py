from __future__ import annotations

import pytest

from zapier.authtoken.models import AuthToken


@pytest.mark.django_db
class TestAuthToken:
    def test_timestamps(self, zapier_token: AuthToken) -> None:
        assert zapier_token.created_at
        assert zapier_token.refreshed_at is None
        assert zapier_token.revoked_at is None
