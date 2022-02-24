from django.db import models
from django.utils.timezone import now as tz_now


class Book(models.Model):

    title = models.CharField(max_length=100)
    author = models.CharField(max_length=100)
    published_at = models.DateTimeField(default=tz_now)

    def __str__(self) -> str:
        return f"{self.title} by {self.author}"
