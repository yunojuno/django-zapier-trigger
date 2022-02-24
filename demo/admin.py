from __future__ import annotations

import logging

from django.contrib import admin

from demo.models import Book

logger = logging.getLogger(__name__)


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    pass
