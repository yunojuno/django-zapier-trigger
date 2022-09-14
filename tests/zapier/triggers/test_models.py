from datetime import timedelta

import pytest

from zapier.triggers.models import TriggerSubscription
from zapier.triggers.models.trigger_event import TriggerEvent


@pytest.mark.django_db
class TestTriggerSubscription:
    def test_unsubscribe(self, subscription: TriggerSubscription) -> None:
        assert subscription.is_active
        subscription.unsubscribe()
        assert subscription.is_inactive
        subscription.refresh_from_db()
        assert subscription.is_inactive
        # just checking this works
        assert str(subscription)

    def test_resubscribe(self, subscription: TriggerSubscription) -> None:
        subscription.unsubscribe()
        subscription.resubscribe("https://www.yahoo.com")
        assert subscription.is_active
        assert subscription.target_url == "https://www.yahoo.com"
        subscription.refresh_from_db()
        assert subscription.is_active
        assert subscription.target_url == "https://www.yahoo.com"

    def test_serialize(self, subscription: TriggerSubscription) -> None:
        assert subscription.serialize() == {
            "active": True,
            "trigger": "foo",
            "url": "https://www.google.com",
            "user_id": subscription.user.pk,
            "uuid": subscription.uuid,
        }


@pytest.mark.django_db
class TestTriggerSubscriptionQuerySet:
    def test_active(self, subscription: TriggerSubscription) -> None:
        assert TriggerSubscription.objects.active().count() == 1
        subscription.unsubscribe()
        assert TriggerSubscription.objects.active().count() == 0

    # @pytest.mark.parametrize("trigger,count", [("foo", 1), ("bar", 0)])
    # def test_trigger(
    #     self, subscription: TriggerSubscription, trigger: str, count: int
    # ) -> None:
    #     assert TriggerSubscription.objects.trigger(trigger).count() == count


@pytest.mark.django_db
class TestTriggerEvent:
    def test_related_names(self, subscription: TriggerSubscription) -> None:
        event = TriggerEvent.objects.create(
            user=subscription.user,
            trigger=subscription.trigger,
            subscription=subscription,
            status_code=200,
        )
        assert list(subscription.trigger_events.all()) == [event]
        assert list(subscription.user.zapier_trigger_events.all()) == [event]
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
