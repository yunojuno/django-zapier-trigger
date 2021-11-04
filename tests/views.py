from typing import Iterable

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import QuerySet

from zapier.views import PollingTriggerView

User = get_user_model()


class UserTriggerView1(PollingTriggerView):
    """Test view that serializes the whole User object."""

    scope = "test_scope"

    def get_queryset(self, user: settings.AUTH_USER_MODEL) -> QuerySet:
        return User.objects.all()


class UserTriggerView2(PollingTriggerView):
    """Test view that serializes a subset of fields."""

    scope = "test_scope"

    def get_queryset(self, user: settings.AUTH_USER_MODEL) -> QuerySet:
        return User.objects.all().values("id", "username")


class UserTriggerSerializer:
    """DRF-like serializer."""

    def __init__(self, data: Iterable, **kwargs: object) -> None:
        self.data = [{"id": obj.id, "full_name": obj.get_full_name()} for obj in data]


class UserTriggerView3(PollingTriggerView):
    """Test view that uses a custom serializer."""

    scope = "test_scope"
    serializer_class = UserTriggerSerializer

    def get_queryset(self, user: settings.AUTH_USER_MODEL) -> QuerySet:
        return User.objects.all()
