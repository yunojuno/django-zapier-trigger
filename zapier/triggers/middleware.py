import json
import logging
import uuid
from typing import Callable

from django.conf import settings
from django.core.exceptions import MiddlewareNotUsed
from django.http import HttpRequest, HttpResponse
from rest_framework.request import Request

logger = logging.getLogger(__name__)


def dump_json(data: bytes) -> str:
    if not data:
        return "(empty)"
    try:
        return json.dumps(json.loads(data), indent=2, sort_keys=True)
    except json.JSONDecodeError:
        logger.exception("Error decoding data")
        return "(error)"


def is_json_request(request: Request) -> bool:
    return "application/json" in request.headers.get("content-type", "")


class JsonRequestDumpMiddleware:
    def __init__(self, get_response: Callable) -> None:
        if not settings.DEBUG:
            raise MiddlewareNotUsed(
                "JsonRequestDumpMiddleware can only run in DEBUG mode."
            )
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        request_id = str(uuid.uuid4()).split("-", 1)[0].upper()
        logger.debug(
            "%s - request headers:\n%s",
            request_id,
            json.dumps(dict(request.headers), indent=2, sort_keys=True),
        )
        if is_json_request(request):
            logger.debug("%s - request body:\n%s", request_id, dump_json(request.body))
        response = self.get_response(request)
        if is_json_request(request):
            logger.debug(
                "%s - response content:\n%s", request_id, dump_json(response.content)
            )
        return response
