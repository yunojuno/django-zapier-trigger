import pytest
from django.conf import settings

from zapier.triggers.models import TriggerSubscription


@pytest.fixture
def subscription(user: settings.AUTH_USER_MODEL) -> TriggerSubscription:
    return TriggerSubscription.objects.create(
        user=user, trigger="foo", target_url="https://www.google.com"
    )


@pytest.mark.django_db
class TestTriggerSubscription:
    def test_unsubscribe(self, subscription: TriggerSubscription) -> None:
        assert subscription.is_active
        subscription.unsubscribe()
        assert subscription.is_inactive
        subscription.refresh_from_db()
        assert subscription.is_inactive

    def test_resubscribe(self, subscription: TriggerSubscription) -> None:
        subscription.unsubscribe()
        subscription.resubscribe("https://www.yahoo.com")
        assert subscription.is_active
        assert subscription.target_url == "https://www.yahoo.com"
        subscription.refresh_from_db()
        assert subscription.is_active
        assert subscription.target_url == "https://www.yahoo.com"
