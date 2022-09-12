import pytest
from django.conf import settings
from rest_framework.authtoken.models import Token

from zapier.triggers.models import TriggerSubscription


@pytest.fixture
def subscription(user: settings.AUTH_USER_MODEL) -> TriggerSubscription:
    return TriggerSubscription.objects.create(
        user=user, trigger="foo", target_url="https://www.google.com"
    )


@pytest.fixture
def active_subscription(active_token: Token) -> TriggerSubscription:
    return TriggerSubscription.objects.create(
        trigger="foo",
        user=active_token.user,
        target_url="https://www.google.com",
    )


@pytest.fixture
def inactive_subscription(active_token: Token) -> TriggerSubscription:
    subscription = TriggerSubscription.objects.create(
        trigger="foo",
        user=active_token.user,
        target_url="https://www.google.com",
    )
    subscription.unsubscribe()
    return subscription
