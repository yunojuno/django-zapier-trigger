from __future__ import annotations

from datetime import datetime

import pytest
from django.utils.timezone import now as tz_now

from zapier.contrib.authtoken.exceptions import TokenAuthError
from zapier.contrib.authtoken.models import AuthToken


@pytest.mark.django_db
class TestAuthToken:
    def test_timestamps(self, active_token: AuthToken) -> None:
        assert active_token.created_at
        assert active_token.refreshed_at is None
        assert active_token.revoked_at is None

    @pytest.mark.parametrize(
        "created_at,refreshed_at,revoked_at,is_active",
        [
            (tz_now(), None, None, True),
            (tz_now(), tz_now(), None, True),
            (tz_now(), tz_now(), tz_now(), False),
            (tz_now(), None, tz_now(), False),
        ],
    )
    def test_is_active(
        self,
        created_at: datetime,
        refreshed_at: datetime | None,
        revoked_at: datetime | None,
        is_active: bool,
    ) -> None:
        token = AuthToken(
            created_at=created_at,
            refreshed_at=refreshed_at,
            revoked_at=revoked_at,
        )
        assert token.is_active == is_active

    def test_refresh(self, active_token: AuthToken) -> None:
        api_key = active_token.api_key
        assert active_token.is_active
        assert active_token.refreshed_at is None
        active_token.refresh()
        assert active_token.is_active
        assert active_token.refreshed_at is not None
        assert active_token.api_key != api_key

    def test_refresh__inactive(self, inactive_token: AuthToken) -> None:
        assert not inactive_token.is_active
        with pytest.raises(TokenAuthError):
            inactive_token.refresh()

    def test_revoke(self, active_token: AuthToken) -> None:
        assert active_token.revoked_at is None
        active_token.revoke()
        assert not active_token.is_active
        assert active_token.revoke is not None

    def test_revoke__inactive(self, inactive_token: AuthToken) -> None:
        # once revoked you cannot re-revoke
        assert not inactive_token.is_active
        assert inactive_token.revoked_at is not None
        with pytest.raises(TokenAuthError):
            inactive_token.revoke()

    def test_reset(self, active_token: AuthToken) -> None:
        api_key = active_token.api_key
        active_token.revoke()
        assert not active_token.is_active
        active_token.reset()
        assert active_token.is_active
        assert active_token.api_key != api_key
