from __future__ import annotations

import json
from uuid import uuid4

import pytest
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.serializers.json import DjangoJSONEncoder

from zapier.models import ZapierToken


@pytest.fixture
def user() -> settings.AUTH_USER_MODEL:
    return get_user_model().objects.create(username=str(uuid4()))


@pytest.fixture
def zapier_token(user: settings.AUTH_USER_MODEL) -> ZapierToken:
    return ZapierToken.objects.create(user=user, api_scopes=["*"])


def jsonify(data: dict) -> dict:
    """Convert a python dict into a JSON-compatible dict."""
    return json.loads(json.dumps(data, cls=DjangoJSONEncoder))
