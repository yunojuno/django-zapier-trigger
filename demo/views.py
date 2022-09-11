import logging

# from django.db.models import QuerySet
from django.http import HttpRequest, JsonResponse

# from demo.models import Film
from demo.models import FilmQuerySet

# from django.shortcuts import render

# from zapier.triggers.views import TriggerSubscriptions

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
