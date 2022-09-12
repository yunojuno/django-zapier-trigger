from typing import Callable

from rest_framework.permissions import BasePermission
from rest_framework.request import Request

from .settings import STRICT_MODE


class IsZapier(BasePermission):
    """
    Enforce STRICT_MODE.

    The User-Agent header for all requests from Zapier is set to
    "Zapier". This is trivial to spoof, so this check doesn't increase
    security in any way, but it's a useful signal in case of casual
    abuse. (Casual = someone probing with no real intent.)

    """

    def has_permission(self, request: Request, view: Callable) -> bool:
        if not STRICT_MODE:
            return True
        return request.headers.get("user-agent", "") == "Zapier"
