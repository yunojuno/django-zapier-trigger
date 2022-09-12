import logging

from rest_framework.request import Request

from demo.models import Film
from zapier.triggers.types import TriggerData

logger = logging.getLogger(__name__)


def new_book(request: Request) -> TriggerData:
    return [
        {"id": 1, "title": "Hot Water", "author": "PG Wodehouse", "published": "1932"},
        {
            "id": 2,
            "title": "Great Expectations",
            "author": "Charles Dickens",
            "published": "1860",
        },
        {
            "id": 3,
            "title": "Moby Dick",
            "author": "Herman Melville",
            "published": "1851",
        },
    ]


def new_films(request: Request) -> TriggerData:
    films = Film.objects.all().order_by("-id")
    return [film.serialize() for film in films]
