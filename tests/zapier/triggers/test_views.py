import pytest
from django.test import Client, RequestFactory
from django.urls import reverse
from rest_framework.authtoken.models import Token
from rest_framework.request import Request

from zapier.triggers.models import TriggerSubscription
from zapier.triggers.settings import get_trigger_data_func
from zapier.triggers.types import TriggerData
from zapier.triggers.views import TriggerView


@pytest.mark.django_db
@pytest.mark.parametrize("prefix,status_code", [("Bearer", 401), ("Token", 200)])
def test_auth_check(
    client: Client, active_token: Token, prefix: str, status_code: int
) -> None:
    url = reverse("zapier_triggers:auth_check")
    response = client.get(url, {}, HTTP_AUTHORIZATION=f"{prefix} {active_token.key}")
    assert response.status_code == status_code


@pytest.mark.django_db
def test_auth_check__missing(client: Client, active_token: Token) -> None:
    url = reverse("zapier_triggers:auth_check")
    response = client.get(url, {})
    assert response.status_code == 401


@pytest.mark.django_db
class TestTriggerView:
    def get_new_book_data(self, request: Request) -> TriggerData:
        return get_trigger_data_func("new_book")(request)

    def test_get(self, rf: RequestFactory, active_token: Token) -> None:
        view = TriggerView.as_view()
        url = reverse("zapier_triggers:list", kwargs={"trigger": "new_book"})
        request = rf.get(url, HTTP_AUTHORIZATION=f"Token {active_token.key}")
        response = view(request, "new_book")
        assert response.status_code == 200
        # implicit assert that one event exists
        event = active_token.user.zapier_trigger_events.get()
        assert event.event_data == self.get_new_book_data(request)

    def test_post(self, rf: RequestFactory, active_token: Token) -> None:
        view = TriggerView.as_view()
        url = reverse("zapier_triggers:subscribe", kwargs={"trigger": "new_book"})
        request = rf.post(
            url,
            data={"hookUrl": "www.foogle.com"},
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Token {active_token.key}",
        )
        response = view(request, "new_book")
        assert response.status_code == 201
        new_subscription = TriggerSubscription.objects.get()
        assert new_subscription.is_active
        assert new_subscription.trigger == "new_book"
        assert new_subscription.user == active_token.user

    def test_delete(
        self,
        rf: RequestFactory,
        active_token: Token,
        active_subscription: TriggerSubscription,
    ) -> None:
        view = TriggerView.as_view()
        url = reverse(
            "zapier_triggers:unsubscribe",
            kwargs={"trigger": "new_book", "subscription_id": active_subscription.uuid},
        )
        request = rf.delete(
            url,
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Token {active_token.key}",
        )
        response = view(request, "new_book", active_subscription.uuid)
        assert response.status_code == 204
        active_subscription.refresh_from_db()
        assert active_subscription.is_inactive
