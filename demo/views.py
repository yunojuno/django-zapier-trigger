import logging

from django.db.models import QuerySet
from django.http import HttpRequest, JsonResponse
from django.shortcuts import render
from django.views.decorators import csrf
from django.views.decorators.http import require_http_methods

from demo.models import Book
from zapier.decorators import zapier_view
from zapier.triggers.polling.decorators import zapier_view_request_log
from zapier.triggers.polling.models import PollingTriggerRequest
from zapier.triggers.polling.views import PollingTriggerView

logger = logging.getLogger(__name__)


def test(request: HttpRequest, number: int) -> JsonResponse:
    return JsonResponse([{"id": i} for i in reversed(range(number))], safe=False)


class NewBooksById(PollingTriggerView):

    scope = "new_books"

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        # noop - just checking it's there
        requests = request.auth.user.zapier_trigger_requests
        qs = Book.objects.exclude(count=0).order_by("-id").values()
        if previous := requests.exclude(count=0).order_by("id").last():
            return qs.filter(id__gt=previous.last_object_id)
        return qs


class NewBooksByTimestamp(NewBooksById):
    def get_queryset(self, request: HttpRequest) -> QuerySet:
        qs = Book.objects.order_by("-id").values()
        if obj := self.get_last_obj(request):
            return qs.filter(published_at__gt=obj["published_at"])
        return qs


@csrf.csrf_exempt
def receive_webhook(request: HttpRequest) -> JsonResponse:
    return JsonResponse({"result": "ok"})


@zapier_view
@zapier_view_request_log("new_books")
def new_books(request: HttpRequest) -> JsonResponse:
    if previous_request := PollingTriggerRequest.objects.previous(
        user=request.user, scope="new_books"
    ):
        last_object_id = previous_request.last_object_id
        logger.debug(
            "Found previous non-zero request; last_object_id=%s", last_object_id
        )
    response = render(request, "zapier/new_book.json", content_type="application/json")
    return response
