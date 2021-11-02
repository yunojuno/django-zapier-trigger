from unittest import mock

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import QuerySet

from zapier.views import PollingTriggerView

User = get_user_model()


class MyTriggerView(PollingTriggerView):

    scope = "test_scope"
    serializer_class = mock.MagicMock()

    def get_queryset(self, user: settings.AUTH_USER_MODEL) -> QuerySet:
        return User.objects.none()
