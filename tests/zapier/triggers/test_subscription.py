import pytest
from django.conf import settings

from zapier.triggers.models.trigger_subscription import TriggerSubscription
from zapier.triggers.subscription import subscribe, unsubscribe


@pytest.mark.django_db
def test_subscribe(user: settings.AUTH_USER_MODEL) -> None:
    subscription = subscribe(user, "foo", "www.google.com")
    assert subscription.is_active
    assert subscription.user == user
    assert subscription.trigger == "foo"
    assert subscription.target_url == "www.google.com"
    assert subscription.pk


@pytest.mark.django_db
def test_resubscribe(inactive_subscription: TriggerSubscription) -> None:
    user = inactive_subscription.user
    trigger = inactive_subscription.trigger
    assert inactive_subscription.is_inactive
    subscribe(user, trigger, "www.yahoo.com")
    inactive_subscription.refresh_from_db()
    assert inactive_subscription.is_active


@pytest.mark.django_db
def test_unsubscribe(subscription: TriggerSubscription) -> None:
    assert subscription.is_active
    unsubscribe(subscription)
    assert subscription.is_inactive
