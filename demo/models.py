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
            "published_at": self.published_at,
        }
