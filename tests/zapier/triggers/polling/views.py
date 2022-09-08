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
from django.http import HttpRequest

from zapier.triggers.polling.views import PollingTriggerView

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

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        return User.objects.exclude(id=request.auth.user_id).order_by("-id")


class UsernameView(UserView):
    """Test view that serializes a subset of fields."""

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        return super().get_queryset(request).values("id", "username")


class FullNameView(UserView):
    """Test view that uses a custom serializer."""

    serializer = FullNameSerializer


class FirstOrLastNameView(UserView):
    """Test view that uses a dynamic serializer."""

    def get_serializer(self, request: HttpRequest) -> Any:
        if request.auth.user.first_name == "Fred":
            return FirstNameSerializer
        return FullNameSerializer
