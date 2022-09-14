from __future__ import annotations

import json
import logging

from django.contrib import admin
from django.core.serializers.json import DjangoJSONEncoder
from django.utils.html import format_html, mark_safe

from .models import TriggerEvent, TriggerSubscription

logger = logging.getLogger(__name__)


def format_json_for_admin(data: dict) -> str:
    """
    Pretty-print JSON data in admin site.

    Take entity context JSON, indent it, order the keys and then present
    it as a <code> block. That's about as good as we can get until
    someone builds a custom syntax function.

    """
    pretty = json.dumps(
        data, cls=DjangoJSONEncoder, sort_keys=True, indent=4, separators=(",", ": ")
    )
    # https://docs.djangoproject.com/en/1.11/ref/utils/#django.utils.html.format_html
    # this is a fudge to get around the fact that we cannot put a <pre> inside a <p>,
    # but we want the <p> formatting (.align CSS). We can either use a <pre> and an
    # inline style to mimic the CSS, or forego the <pre> and put the spaces
    # and linebreaks in as HTML.
    pretty = pretty.replace(" ", "&nbsp;").replace("\n", "<br/>")
    return format_html("<code>{}</code>", mark_safe(pretty))


@admin.register(TriggerSubscription)
class TriggerSubscriptionAdmin(admin.ModelAdmin):
    list_display = ("user", "trigger", "zap", "subscribed_at", "_is_active")
    readonly_fields = (
        "user",
        "trigger",
        "zap",
        "target_url",
        "subscribed_at",
        "unsubscribed_at",
        "uuid",
    )

    @admin.display(boolean=True)
    def _is_active(self, obj: TriggerSubscription) -> bool:
        return obj.is_active


@admin.register(TriggerEvent)
class TriggerEventAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "trigger",
        "http_method",
        "started_at",
        "duration",
        "status_code",
        # "status",
    )
    readonly_fields = (
        "user",
        "trigger",
        "http_method",
        "started_at",
        "finished_at",
        "duration",
        "subscription",
        "status_code",
        "_event_data",
    )
    exclude = ("event_data",)
    raw_id_fields = ("user", "subscription")
    search_fields = (
        "user__first_name",
        "user__last_name",
    )

    @admin.display(description="Event data")
    def _event_data(self, obj: TriggerEvent) -> str:
        return format_json_for_admin(obj.event_data)
