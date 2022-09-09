import logging

from django.db.models import QuerySet
from django.http import HttpRequest, JsonResponse
from django.shortcuts import render

from demo.models import Film, FilmQuerySet
from zapier.decorators import zapier_auth
from zapier.triggers.polling.decorators import zapier_view_request_log
from zapier.triggers.polling.models import PollingTriggerRequest
from zapier.triggers.polling.views import PollingTriggerView

logger = logging.getLogger(__name__)


def test(request: HttpRequest, number: int) -> JsonResponse:
    return JsonResponse([{"id": i} for i in reversed(range(number))], safe=False)


class FilmSerializer:
    def __init__(self, films: FilmQuerySet, many: bool = True) -> None:
        self.films = films
        self.many = many

    @property
    def data(self) -> list[dict]:
        return [film.serialize() for film in self.films]


class NewFilms(PollingTriggerView):

    trigger = "new_films"
    serializer = FilmSerializer

    def get_queryset(self, request: HttpRequest, cursor_id: str | None) -> QuerySet:
        qs = Film.objects.all()
        if cursor_id:
            return qs.filter(id__gt=cursor_id)
        return qs.order_by("-id")


@zapier_auth
@zapier_view_request_log("new_films")
def new_films(request: HttpRequest) -> JsonResponse:
    if cursor_id := PollingTriggerRequest.objects.cursor_id(request.user, "new_films"):
        logger.debug("Found previous non-zero request; last_object_id=%s", cursor_id)
    response = render(request, "zapier/new_films.json", content_type="application/json")
    return response
