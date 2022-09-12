from unittest import mock

import pytest
from django.test import RequestFactory

from zapier.triggers.permissions import IsZapier


@pytest.mark.parametrize(
    "strict_mode,user_agent,has_permission",
    [
        (True, "Zapier", True),
        (True, "Not-Zapier", False),
        (False, "Zapier", True),
        (False, "Not-Zapier", True),
    ],
)
def test_is_zapier(
    rf: RequestFactory, strict_mode: bool, user_agent: str, has_permission: bool
) -> None:
    request = rf.get("/", HTTP_USER_AGENT=user_agent)
    perm = IsZapier()
    with mock.patch("zapier.triggers.permissions.STRICT_MODE", strict_mode):
        assert perm.has_permission(request, None) == has_permission
