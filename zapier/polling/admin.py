from __future__ import annotations

import json
import logging

from django.contrib import admin
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import QuerySet
from django.http import HttpRequest
from django.utils.html import format_html, mark_safe

from zapier.polling.models import PollingTriggerRequest

logger = logging.getLogger(__name__)


def format_json_for_admin(context: dict) -> str:
    """
    Pretty-print formatted context JSON.

    Take entity context JSON, indent it, order the keys and then
    present it as a <code> block. That's about as good as we can get
    until someone builds a custom syntax function.

    """
    pretty = json.dumps(
        context,
        cls=DjangoJSONEncoder,
        sort_keys=True,
        indent=4,
        separators=(",", ": "),
    )
    # https://docs.djangoproject.com/en/1.11/ref/utils/#django.utils.html.format_html
    # this is a fudge to get around the fact that we cannot put a <pre> inside a <p>,
    # but we want the <p> formatting (.align CSS). We can either use a <pre> and an
    # inline style to mimic the CSS, or forego the <pre> and put the spaces
    # and linebreaks in as HTML.
    pretty = pretty.replace(" ", "&nbsp;").replace("\n", "<br/>")
    return format_html("<code>{}</code>", mark_safe(pretty))


class PollingTriggerRequestInline(admin.TabularInline):
    max_num = 0
    model = PollingTriggerRequest
    exclude = ("data",)
    readonly_fields = ("timestamp", "scope", "count")
    verbose_name_plural = "Most recent polling trigger requests"

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        ids = PollingTriggerRequest.objects.all().values_list("id", flat=True)[:5]
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
