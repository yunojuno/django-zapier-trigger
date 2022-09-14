from unittest import mock

import pytest

from zapier.triggers.event import push
from zapier.triggers.models.trigger_subscription import TriggerSubscription


@pytest.mark.django_db
@mock.patch("zapier.triggers.event.requests")
def test_push(mock_requests, active_subscription: TriggerSubscription) -> None:
    event_data = {"foo": "Bar"}
    # fake a POST that returns a 201
    mock_requests.post.return_value = mock.Mock(status_code=201)
    event = push(active_subscription, event_data)
    assert event.user == active_subscription.user
    assert event.trigger == active_subscription.trigger
    assert event.subscription == active_subscription
    assert event.started_at
    assert event.finished_at
    assert event.duration == event.finished_at - event.started_at
    assert event.http_method == "POST"
    assert event.status_code == 201
