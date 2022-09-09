import logging

from django.db.models import QuerySet
from django.http import HttpRequest, JsonResponse
from django.shortcuts import render

from demo.models import Book
from zapier.decorators import zapier_auth
from zapier.triggers.polling.decorators import zapier_view_request_log
from zapier.triggers.polling.models import PollingTriggerRequest
from zapier.triggers.polling.views import PollingTriggerView

logger = logging.getLogger(__name__)


def test(request: HttpRequest, number: int) -> JsonResponse:
    return JsonResponse([{"id": i} for i in reversed(range(number))], safe=False)


class NewFilms(PollingTriggerView):

    trigger = "new_films"

    def get_queryset(self, request: HttpRequest, cursor_id: str | None) -> QuerySet:
        # noop - just checking it's there
        assert request.auth.user.zapier_trigger_requests  # noqa: S101
        qs = Book.objects.order_by("-id").values()
        if cursor_id:
            return qs.filter(id__gt=cursor_id)
        return qs


@zapier_auth
@zapier_view_request_log("new_films")
def new_films(request: HttpRequest) -> JsonResponse:
    if cursor_id := PollingTriggerRequest.objects.cursor_id(request.user, "new_films"):
        logger.debug("Found previous non-zero request; last_object_id=%s", cursor_id)
    response = render(request, "zapier/new_films.json", content_type="application/json")
    return response
