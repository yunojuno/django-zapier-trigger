import pytest
from django.contrib.auth import get_user_model

from zapier.models import ZapierToken


@pytest.fixture
def zapier_token() -> ZapierToken:
    user = get_user_model().objects.create()
    return ZapierToken.objects.create(user=user, api_scopes=["*"])
