"""
A set of user views that can be used in tests:

1. UserView - returns all users, has no serializer - FAILS
2. UsernameView - subclass UserView, uses QuerySet.values(...)
3. FullNameView - subclass UserView, uses FullNameSerializer
4. FirstOrLastNameView - subclass UserView, return FirstNameSerializer or
    FullNameSerializer based on request.user

"""
from __future__ import annotations

from typing import Any, Iterable

from django.contrib.auth import get_user_model
from django.db.models import QuerySet

from zapier.views import PollingTriggerView

User = get_user_model()


class FullNameSerializer:
    """Serializes full_name."""

    def __init__(self, data: Iterable, **kwargs: object) -> None:
        self.data = [{"id": obj.id, "full_name": obj.get_full_name()} for obj in data]


class FirstNameSerializer:
    """Serializes first_name."""

    def __init__(self, data: Iterable, **kwargs: object) -> None:
        self.data = [{"id": obj.id, "first_name": obj.first_name} for obj in data]


class UserView(PollingTriggerView):
    """Test view that serializes the whole User object - FAILS."""

    scope = "test_scope"

    def get_queryset(self) -> QuerySet:
        return User.objects.all()


class UsernameView(UserView):
    """Test view that serializes a subset of fields."""

    sort_key = lambda obj: obj["username"]

    def get_queryset(self) -> QuerySet:
        return User.objects.exclude(id=self.token.user_id).values("id", "username")


class ReverseUsernameView(UsernameView):
    """Test view that serializes a subset of fields in reverse order."""

    sort_reverse = False


class FullNameView(UserView):
    """Test view that uses a custom serializer."""

    serializer_class = FullNameSerializer


class FirstOrLastNameView(UserView):
    """Test view that uses a dynamic serializer."""

    def get_serializer(self) -> Any:
        if self.token.user.first_name == "Fred":
            return FirstNameSerializer
        return FullNameSerializer
