# import json

# import pytest
# from django.test import Client
# from django.urls import reverse
# from rest_framework.authtoken.models import Token

# from zapier.triggers.models import TriggerSubscription


# @pytest.mark.django_db
# def test_subscribe(client: Client, active_token: Token) -> None:
#     url = reverse("zapier_triggers:subscribe", kwargs={"trigger": "foo"})
#     assert TriggerSubscription.objects.count() == 0
#     response = client.post(
#         url,
#         {"hookUrl": "https://www.google.com"},
#         content_type="application/json",
#         HTTP_AUTHORIZATION=active_token.http_authorization,
#     )
#     assert response.status_code == 201, response.content
#     # implicit assert that there is one subscription
#     subscription = TriggerSubscription.objects.get()
#     assert subscription.target_url == "https://www.google.com"
#     assert subscription.trigger == "foo"
#     assert subscription.user == active_token.user
#     assert subscription.is_active


# @pytest.mark.django_db
# def test_resubscribe(
#     client: Client, inactive_subscription: TriggerSubscription
# ) -> None:
#     url = reverse("zapier_triggers:subscribe", kwargs={"trigger": "foo"})
#     active_token = Token.objects.get(user=inactive_subscription.user)
#     response = client.post(
#         url,
#         {"hookUrl": "https://www.google.com"},
#         content_type="application/json",
#         HTTP_AUTHORIZATION=active_token.http_authorization,
#     )
#     assert response.status_code == 201, response.content
#     # implicit assert that there is one subscription
#     subscription = TriggerSubscription.objects.get()
#     assert subscription.target_url == "https://www.google.com"
#     assert subscription.trigger == "foo"
#     assert subscription.user == active_token.user
#     assert subscription.is_active


# @pytest.mark.django_db
# def test_unsubscribe(client: Client, active_subscription: TriggerSubscription) -> None:
#     url = reverse(
#         "zapier_triggers:unsubscribe",
#         kwargs={
#             "trigger": active_subscription.trigger,
#             "subscription_id": active_subscription.uuid,
#         },
#     )
#     active_token = Token.objects.get(user=active_subscription.user)
#     assert active_subscription.is_active
#     assert not active_subscription.is_inactive
#     response = client.delete(
#         url,
#         {"hookUrl": "https://www.google.com"},
#         content_type="application/json",
#         HTTP_AUTHORIZATION=active_token.http_authorization,
#     )
#     assert response.status_code == 204
#     active_subscription.refresh_from_db()
#     assert not active_subscription.is_active
#     assert active_subscription.is_inactive


# @pytest.mark.django_db
# def test_list(client: Client, active_token: Token) -> None:
#     url = reverse(
#         "zapier_triggers:list",
#         kwargs={"trigger": "new_hook"},
#     )
#     response = client.get(
#         url,
#         {"hookUrl": "https://www.google.com"},
#         content_type="application/json",
#         HTTP_AUTHORIZATION=active_token.http_authorization,
#     )
#     assert response.status_code == 200
#     assert json.loads(response.content.decode()) == {"result": "OK"}
