from __future__ import annotations

import logging

from django.contrib import admin
from django.http import HttpRequest

from demo.models import Book, BookQuerySet
from zapier.triggers.hooks.models import RestHookSubscription

logger = logging.getLogger(__name__)


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):

    actions = ["fire_webhook"]

    @admin.action(description='Push a "new book" notification to subscribers')
    def fire_webhook(self, request: HttpRequest, queryset: BookQuerySet) -> None:
        subscriptions = RestHookSubscription.objects.active().filter(scope="new_book")
        subs_count = subscriptions.count()
        books = [b.serialize() for b in queryset]
        books_count = len(books)
        for s in subscriptions:
            for b in books:
                s.push(b)
        self.message_user(
            request,
            f"Sent {books_count} new books to {subs_count} subscribers.",
            "success",
        )
