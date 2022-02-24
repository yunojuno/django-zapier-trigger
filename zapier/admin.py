from __future__ import annotations

import datetime
import decimal
import json
import logging

from django.contrib import admin, messages
from django.db.models import QuerySet
from django.http import HttpRequest
from django.utils.html import format_html, mark_safe
from django.utils.translation import gettext as _
from django.utils.translation import gettext_lazy as _lazy

from zapier.models import ZapierToken, ZapierTokenRequest

logger = logging.getLogger(__name__)


def format_json_for_admin(context: dict) -> str:
    """
    Pretty-print formatted context JSON.

    Take entity context JSON, indent it, order the keys and then
    present it as a <code> block. That's about as good as we can get
    until someone builds a custom syntax function.

    """
    # noqa: pydocstyle no blank line
    def _clean(val: decimal.Decimal | datetime.date | datetime.datetime) -> float | str:
        """Convert unserializable values into serializable versions."""
        if type(val) is decimal.Decimal:
            return float(val)
        if type(val) is datetime.date:
            return val.isoformat()
        if type(val) is datetime.datetime:
            return val.isoformat()
        raise TypeError("Unserializable JSON value: %s" % val)

    pretty = json.dumps(
        context, sort_keys=True, indent=4, separators=(",", ": "), default=_clean
    )
    # https://docs.djangoproject.com/en/1.11/ref/utils/#django.utils.html.format_html
    # this is a fudge to get around the fact that we cannot put a <pre> inside a <p>,
    # but we want the <p> formatting (.align CSS). We can either use a <pre> and an
    # inline style to mimic the CSS, or forego the <pre> and put the spaces
    # and linebreaks in as HTML.
    pretty = pretty.replace(" ", "&nbsp;").replace("\n", "<br/>")
    return format_html("<code>{}</code>", mark_safe(pretty))


@admin.register(ZapierToken)
class ZapierTokenAdmin(admin.ModelAdmin):
    actions = ("refresh_tokens", "reset_tokens", "revoke_tokens")
    list_display = ("user", "api_token", "api_scopes")
    search_fields = ("user__first_name", "user__last_name", "user__email", "api_scopes")
    list_select_related = ("user",)
    readonly_fields = (
        "api_token",
        # "request_log",
        "created_at",
        "last_updated_at",
    )
    raw_id_fields = ("user",)

    def refresh_tokens(self, request: HttpRequest, queryset: QuerySet) -> None:
        for token in queryset:
            token.refresh()
        self.message_user(
            request,
            _("Successfully refreshed selected zapier tokens"),
            messages.SUCCESS,
        )

    refresh_tokens.short_description = _lazy(  # type: ignore
        "Refresh selected zapier tokens (reset token uuid, retain logs, scopes)"
    )

    def reset_tokens(self, request: HttpRequest, queryset: QuerySet) -> None:
        for token in queryset:
            token.reset()
        self.message_user(
            request,
            _("Successfully reset selected zapier tokens"),
            messages.SUCCESS,
        )

    reset_tokens.short_description = _lazy(  # type: ignore
        "Reset selected zapier tokens (reset logs, retain token uuid, scopes)"
    )

    def revoke_tokens(self, request: HttpRequest, queryset: QuerySet) -> None:
        for token in queryset:
            token.revoke()
        self.message_user(
            request,
            _("Successfully revoked selected zapier tokens"),
            messages.SUCCESS,
        )

    revoke_tokens.short_description = _lazy(  # type: ignore
        "Revoke selected zapier tokens (remove scopes, retain token uuid, logs)"
    )


@admin.register(ZapierTokenRequest)
class ZapierTokenRequestAdmin(admin.ModelAdmin):
    list_display = ("token", "timestamp", "count")
    exclude = ("data",)
    readonly_fields = ("pretty_data",)

    def has_change_permission(
        self, request: HttpRequest, obj: ZapierTokenRequest | None = None
    ) -> bool:
        return False

    @admin.display(description="Data (formatted)")
    def pretty_data(self, obj: ZapierTokenRequest) -> str:
        return format_json_for_admin(obj.data)
