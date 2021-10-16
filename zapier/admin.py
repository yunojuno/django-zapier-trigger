from __future__ import annotations

import logging

from django.contrib import admin, messages
from django.db.models import QuerySet
from django.http import HttpRequest
from django.utils.translation import gettext as _
from django.utils.translation import gettext_lazy as _lazy

from zapier.models import ZapierToken

logger = logging.getLogger(__name__)


@admin.register(ZapierToken)
class ZapierTokenAdmin(admin.ModelAdmin):
    actions = ("refresh_tokens", "reset_tokens", "revoke_tokens")
    list_display = ("user", "api_token", "api_scopes")
    search_fields = ("user__first_name", "user__last_name", "user__email", "api_scopes")
    list_select_related = ("user",)
    readonly_fields = (
        "api_token",
        "request_log",
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
