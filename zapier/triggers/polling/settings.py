from typing import Callable

from django.conf import settings
from django.http import HttpRequest, JsonResponse

from zapier.settings import import_func

# max number of objects to return
DEFAULT_PAGE_SIZE = getattr(settings, "ZAPIER_TRIGGER_DEFAULT_PAGE_SIZE", 25)

# dict mapping trigger scope to a view function
VIEW_FUNC_MAP = getattr(settings, "ZAPIER_TRIGGER_VIEW_FUNC_MAP", {})


def get_view_func(scope: str) -> Callable[[HttpRequest, str], JsonResponse]:
    """Convert VIEW_FUNC_MAP value into the Callable it references."""
    return import_func(VIEW_FUNC_MAP[scope])


# value of None, "ALL", or "NON_ZERO" (default) that determines how a
# polling request is logged.
TRIGGER_REQUEST_LOG = getattr(settings, "ZAPIER_TRIGGER_REQUEST_LOG", "NON_ZERO")
