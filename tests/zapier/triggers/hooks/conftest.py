import pytest

from zapier.contrib.authtoken.models import AuthToken
from zapier.triggers.hooks.models import RestHookSubscription


@pytest.fixture
def active_subscription(active_token: AuthToken) -> RestHookSubscription:
    return RestHookSubscription.objects.create(
        scope="foo",
        user=active_token.user,
        target_url="https://www.google.com",
    )


@pytest.fixture
def inactive_subscription(active_token: AuthToken) -> RestHookSubscription:
    subscription = RestHookSubscription.objects.create(
        scope="foo",
        user=active_token.user,
        target_url="https://www.google.com",
    )
    subscription.unsubscribe()
    return subscription
