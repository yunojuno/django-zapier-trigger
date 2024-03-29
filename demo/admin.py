from __future__ import annotations

import logging

from django.contrib import admin
from django.http import HttpRequest

from demo.models import Book, BookQuerySet, Film
from zapier.triggers.event import push
from zapier.triggers.models import TriggerSubscription

logger = logging.getLogger(__name__)


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    pass
    actions = ["fire_webhook"]

    @admin.action(description='Push a "new book" notification to subscribers')
    def fire_webhook(self, request: HttpRequest, queryset: BookQuerySet) -> None:
        subscriptions = TriggerSubscription.objects.active().filter(trigger="new_book")
        subs_count = subscriptions.count()
        if not subs_count:
            self.message_user(request, "No subscribers found.", "warning")
            return
        books: list[dict] = [b.serialize() for b in queryset]
        books_count = len(books)
        for s in subscriptions:
            for b in books:
                push(s, b)
        self.message_user(
            request,
            f"Sent {books_count} new books to {subs_count} subscribers.",
            "success",
        )


@admin.register(Film)
class FilmAdmin(admin.ModelAdmin):
    pass
