from __future__ import annotations

import json
from functools import wraps
from typing import Any, Callable

from django.http import HttpRequest, HttpResponse, HttpResponseForbidden

from zapier.auth import authenticate_request
from zapier.exceptions import TokenAuthError


def parse_content_id(response: HttpResponse) -> int | None:
    """
    Return the id of the first object in the response.

    This function assumes that the HttpResponse.content is a valid serialized
    JSON list of dicts, each of which contains an 'id' property. This is the
    mandated format for a Zapier trigger.

    See https://platform.zapier.com/docs/triggers

    """
    try:
        data = json.loads(response.content)
        return int(data[0]["id"])
    except json.decoder.JSONDecodeError:
        return None
    except IndexError:
        return None
    except AttributeError:
        return None


def zapier_trigger(scope: str) -> Callable:
    """
    Decorate view functions that require ZapierToken authentication.

    If a scope is passed in (anything other than "*") then the token.api_scopes
    is checked.

    After the inner view function is called the request is logged using the
    request.auth.log_request method.

    Returns 403 response if the token is invalid.

    """

    def decorator(view_func: Callable) -> Callable:
        @wraps(view_func)
        def inner(request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
            try:
                authenticate_request(request)
                request.auth.check_scope(scope)
            except TokenAuthError as ex:
                return HttpResponseForbidden(ex)
            resp = view_func(request, *args, **kwargs)
            request.auth.log_request(scope, parse_content_id(resp))
            return resp

        return inner

    return decorator
