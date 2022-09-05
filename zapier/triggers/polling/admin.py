from __future__ import annotations

import logging

from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest

from zapier.utils.admin import format_json_for_admin

from .models import PollingTriggerRequest

logger = logging.getLogger(__name__)


class PollingTriggerRequestInline(admin.TabularInline):
    max_num = 0
    model = PollingTriggerRequest
    exclude = ("data",)
    readonly_fields = ("timestamp", "scope", "count")
    verbose_name_plural = "Most recent polling trigger requests"

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        ids = PollingTriggerRequest.objects.all().values_list("id", flat=True)[:10]
        return PollingTriggerRequest.objects.filter(id__in=ids).order_by("-id")

    def has_delete_permission(
        self, request: HttpRequest, obj: PollingTriggerRequest
    ) -> bool:
        return False


@admin.register(PollingTriggerRequest)
class PollingTriggerRequestAdmin(admin.ModelAdmin):
    list_display = ("token_value", "token_user", "scope", "timestamp", "count")
    list_filter = ("scope", "timestamp")
    exclude = ("data",)
    readonly_fields = ("pretty_data",)

    def has_change_permission(
        self, request: HttpRequest, obj: PollingTriggerRequest | None = None
    ) -> bool:
        return False

    @admin.display(description="Data (formatted)")
    def pretty_data(self, obj: PollingTriggerRequest) -> str:
        return format_json_for_admin(obj.data)

    @admin.display()
    def token_value(self, obj: PollingTriggerRequest) -> str:
        return obj.token.api_token

    @admin.display()
    def token_user(self, obj: PollingTriggerRequest) -> str:
        return obj.token.user
