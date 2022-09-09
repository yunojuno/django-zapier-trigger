from __future__ import annotations

import logging

from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest

from zapier.admin import format_json_for_admin

from .models import RestHookEvent, RestHookSubscription

logger = logging.getLogger(__name__)


class RestHookEventInline(admin.TabularInline):
    max_num = 0
    model = RestHookEvent
    readonly_fields = ("started_at", "finished_at", "duration", "status_code")
    exclude = ("request_payload", "response_payload")
    verbose_name_plural = "Most recent webhook events"

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        # We cannot use a slice in the return QS as the admin app tries to
        # apply its own filters and you can't filter a sliced queryset.
        # To get around this we extract the ids of the most recent objects
        # and then filter on those - in effect getting the last X objects.
        ids = RestHookEvent.objects.order_by("-id").values_list("id", flat=True)[:10]
        return RestHookEvent.objects.filter(id__in=ids).order_by("-id")

    def has_delete_permission(self, request: HttpRequest, obj: RestHookEvent) -> bool:
        return False


@admin.register(RestHookSubscription)
class RestHookSubscriptionAdmin(admin.ModelAdmin):
    list_display = ("user", "trigger", "subscribed_at", "_is_active")
    readonly_fields = (
        "user",
        "trigger",
        "target_url",
        "subscribed_at",
        "unsubscribed_at",
        "uuid",
    )
    inlines = (RestHookEventInline,)

    @admin.display(boolean=True)
    def _is_active(self, obj: RestHookSubscription) -> bool:
        return obj.is_active


@admin.register(RestHookEvent)
class RestHookEventAdmin(admin.ModelAdmin):
    def get_queryset(self, request: HttpRequest) -> QuerySet:
        return super().get_queryset(request).select_related("subscription__user")

    list_display = (
        "subscription",
        "subscriber",
        "started_at",
        "duration",
        "status_code",
        "status",
    )
    readonly_fields = (
        "subscription",
        "started_at",
        "finished_at",
        "duration",
        "status_code",
        "status",
        "request_data",
        "response_data",
    )
    exclude = ("request_payload", "response_payload")
    search_fields = (
        "subscription__user__first_name",
        "subscription__user__last_name",
    )

    @admin.display(description="Subscriber")
    def subscriber(self, obj: RestHookEvent) -> str:
        return obj.subscription.user.get_full_name()

    @admin.display(description="Request data")
    def request_data(self, obj: RestHookEvent) -> str:
        return format_json_for_admin(obj.request_payload)

    @admin.display(description="Response data")
    def response_data(self, obj: RestHookEvent) -> str:
        return format_json_for_admin(obj.response_payload)
