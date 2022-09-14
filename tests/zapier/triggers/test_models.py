from datetime import timedelta

import pytest
from django.conf import settings as django_settings

from zapier.triggers.models import TriggerSubscription
from zapier.triggers.models.trigger_event import TriggerEvent
from zapier.triggers.models.trigger_subscription import TriggerSubscriptionError


@pytest.mark.django_db
class TestTriggerSubscriptionQuerySet:
    def test_active(self, active_subscription: TriggerSubscription) -> None:
        assert TriggerSubscription.objects.active().count() == 1

    def test_active__empty(self, inactive_subscription: TriggerSubscription) -> None:
        assert TriggerSubscription.objects.active().count() == 0


@pytest.mark.django_db
class TestTriggerSubscriptionManager:
    def test_subscriber(self, user: django_settings.AUTH_USER_MODEL) -> None:
        TriggerSubscription.objects.subscribe(
            user=user,
            trigger="foo",
            zap="subscription:123",
            target_url="www.foogle.com",
        )
        with pytest.raises(TriggerSubscriptionError):
            TriggerSubscription.objects.subscribe(
                user=user,
                trigger="foo",
                zap="subscription:123",
                target_url="www.foogle.com",
            )


@pytest.mark.django_db
class TestTriggerSubscription:
    def test_unsubscribe(self, active_subscription: TriggerSubscription) -> None:
        assert active_subscription.is_active
        active_subscription.unsubscribe()
        assert active_subscription.is_inactive
        active_subscription.refresh_from_db()
        assert active_subscription.is_inactive
        # just checking this works
        assert str(active_subscription)

    def test_serialize(self, active_subscription: TriggerSubscription) -> None:
        assert active_subscription.serialize() == {
            "active": True,
            "trigger": "foo",
            "url": "https://www.google.com",
            "user_id": active_subscription.user.pk,
            "uuid": active_subscription.uuid,
            "zap": active_subscription.zap,
        }


@pytest.mark.django_db
class TestTriggerEvent:
    def test_related_names(self, active_subscription: TriggerSubscription) -> None:
        event = TriggerEvent.objects.create(
            user=active_subscription.user,
            trigger=active_subscription.trigger,
            subscription=active_subscription,
            status_code=200,
        )
        assert list(active_subscription.trigger_events.all()) == [event]
        assert list(active_subscription.user.zapier_trigger_events.all()) == [event]
        assert str(event)

    def test_duration(self) -> None:
        # this object can't be saved as it's missing FKs, but these are not
        # relevant to the duration property.
        event = TriggerEvent()
        assert event.started_at is not None
        assert event.finished_at is None
        assert event.duration is None
        event.finished_at = event.started_at + timedelta(seconds=1)
        assert event.duration == timedelta(seconds=1)
