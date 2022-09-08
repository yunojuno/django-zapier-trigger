from django.db import models
from django.utils.timezone import now as tz_now


class BookQuerySet(models.QuerySet):
    pass


class Book(models.Model):

    title = models.CharField(max_length=100)
    author = models.CharField(max_length=100)
    published_at = models.DateTimeField(default=tz_now)

    objects = BookQuerySet.as_manager()

    def __str__(self) -> str:
        return f"{self.title} by {self.author}"

    def serialize(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "author": self.author,
            "published": self.published_at.year,
        }


class FilmQuerySet(models.QuerySet):
    pass


class Film(models.Model):

    title = models.CharField(max_length=100)
    director = models.CharField(max_length=100)
    release_date = models.DateField()

    objects = FilmQuerySet.as_manager()

    def __str__(self) -> str:
        return f"{self.title} by {self.director} ({self.release_date.year})"

    def serialize(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "director": self.director,
            "release_date": self.released_date,
        }
