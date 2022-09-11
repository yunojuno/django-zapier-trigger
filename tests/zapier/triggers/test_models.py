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

    # def test_push(self, subscription: TriggerSubscription) -> None:
    #     with mock.patch("zapier.triggers.submodels.requests") as mock_requests:
    #         mock_response = mock.Mock()
    #         mock_response.status_code = 200
    #         mock_response.json.return_value = {"result": "OK"}
    #         mock_requests.post.return_value = mock_response
    #         event = subscription.push([{"foo": "bar"}])
    #     assert event.status_code == 200
    #     assert event.request_payload == [{"foo": "bar"}]
    #     assert event.is_complete
    #     assert event.duration
