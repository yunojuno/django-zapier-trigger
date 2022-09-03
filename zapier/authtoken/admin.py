from __future__ import annotations

import logging

from django.contrib import admin, messages
from django.db.models import QuerySet
from django.http import HttpRequest
from django.utils.translation import gettext as _
from django.utils.translation import gettext_lazy as _lazy

from .models import AuthToken, TokenAuthRequest

logger = logging.getLogger(__name__)


class TokenAuthRequestInline(admin.TabularInline):
    max_num = 0
    model = TokenAuthRequest
    readonly_fields = ["timestamp"]
    verbose_name_plural = "Most recent token auth requests"

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        ids = TokenAuthRequest.objects.all().values_list("id", flat=True)[:5]
        return TokenAuthRequest.objects.filter(id__in=ids).order_by("-id")

    def has_delete_permission(
        self, request: HttpRequest, obj: TokenAuthRequest
    ) -> bool:
        return False


@admin.register(AuthToken)
class AuthTokenAdmin(admin.ModelAdmin):
    actions = ("refresh_tokens", "reset_tokens", "revoke_tokens")
    inlines = (TokenAuthRequestInline,)
    list_display = ("user", "api_token", "api_scopes")
    list_select_related = ("user",)
    readonly_fields = ("api_token", "created_at", "last_updated_at")
    raw_id_fields = ("user",)
    search_fields = ("user__first_name", "user__last_name", "user__email", "api_scopes")

    @admin.display(
        description=_lazy(
            "Refresh selected zapier tokens (reset token uuid, retain logs, scopes)"
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
            "Reset selected zapier tokens (reset logs, retain token uuid, scopes)"
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
            "Revoke selected zapier tokens (remove scopes, retain token uuid, logs)"
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


@admin.register(TokenAuthRequest)
class TokenAuthAdmin(admin.ModelAdmin):
    list_display = ("id", "token_value", "token_user", "timestamp")
    list_filter = ("timestamp",)

    def has_change_permission(
        self, request: HttpRequest, obj: TokenAuthRequest | None = None
    ) -> bool:
        return False

    @admin.display()
    def token_value(self, obj: TokenAuthRequest) -> str:
        return obj.token.api_token

    @admin.display()
    def token_user(self, obj: TokenAuthRequest) -> str:
        return obj.token.user
