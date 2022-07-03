from __future__ import annotations

import logging

from django.contrib import admin, messages
from django.db.models import QuerySet
from django.http import HttpRequest
from django.utils.translation import gettext as _
from django.utils.translation import gettext_lazy as _lazy

from .models import AuthToken

logger = logging.getLogger(__name__)


@admin.register(AuthToken)
class AuthTokenAdmin(admin.ModelAdmin):
    actions = ("refresh_tokens", "reset_tokens", "revoke_tokens")
    list_display = ("user", "api_key")
    list_select_related = ("user",)
    readonly_fields = ("api_key", "created_at", "refreshed_at", "revoked_at")
    raw_id_fields = ("user",)
    search_fields = ("user__first_name", "user__last_name", "user__email")

    @admin.display(
        description=_lazy(
            "Refresh selected zapier tokens (reset token uuid, retain logs, triggers)"
        )
    )
    def refresh_tokens(self, request: HttpRequest, queryset: QuerySet) -> None:
        for token in queryset:
            token.refresh()
        self.message_user(
            request,
            _("Successfully refreshed selected zapier tokens"),
            messages.SUCCESS,
        )

    @admin.display(
        description=_lazy(
            "Reset selected zapier tokens (reset logs, retain token uuid, triggers)"
        )
    )
    def reset_tokens(self, request: HttpRequest, queryset: QuerySet) -> None:
        for token in queryset:
            token.requests.all().delete()
        self.message_user(
            request,
            _("Successfully reset selected zapier tokens"),
            messages.SUCCESS,
        )

    @admin.display(
        description=_lazy(
            "Revoke selected zapier tokens (remove triggers, retain token uuid, logs)"
        )
    )
    def revoke_tokens(self, request: HttpRequest, queryset: QuerySet) -> None:
        for token in queryset:
            token.revoke()
        self.message_user(
            request,
            _("Successfully revoked selected zapier tokens"),
            messages.SUCCESS,
        )
