"""TokenAdmin"""


# Built-in
from datetime import datetime, timezone

# Django
from django.contrib import admin
from django.db.models import Q

# Personal
from jklib.django.db.admins import CannotAddMixin, CannotEditMixin

# Local
from ..models import SecurityToken


# --------------------------------------------------------------------------------
# > Filters
# --------------------------------------------------------------------------------
class IsExpiredFilter(admin.SimpleListFilter):
    """Boolean filter based around the 'expired_at' field"""

    title = "Expired"
    parameter_name = "expired"

    def lookups(self, request, model_admin):
        """
        List of (value, label) for our filter options
        :param Request request:
        :param model_admin:
        :return: List values/labels for this filter
        :rtype: [tuple()]
        """
        return [(None, "All"), (True, "Yes"), (False, "No")]

    def queryset(self, request, queryset):
        """
        Filters the tokens by comparing 'expired_at' to the current timestamp
        :param Request request:
        :param Queryset queryset:
        :return: The updated queryset after we applied our filter
        :rtype: Queryset
        """
        now = datetime.now(timezone.utc)
        if self.value() is None:
            return queryset
        elif self.value():
            return queryset.filter(expired_at__lt=now)
        else:
            return queryset.filter(expired_at__gte=now)


class IsUsedFilter(admin.SimpleListFilter):
    """Boolean filtered based around the 'used_at' field"""

    title = "Used"
    parameter_name = "used"

    def lookups(self, request, model_admin):
        """
        List of (value, label) for our filter options
        :param Request request:
        :param model_admin:
        :return: List values/labels for this filter
        :rtype: [tuple()]
        """
        return [(None, "All"), (True, "Yes"), (False, "No")]

    def queryset(self, request, queryset):
        """
        Filters the tokens checking the value in the 'used_at' field
        :param Request request:
        :param Queryset queryset:
        :return: The updated queryset after we applied our filter
        :rtype: Queryset
        """
        if self.value() is None:
            return queryset
        elif self.value():
            return queryset.filter(~Q(used_at=None))
        else:
            return queryset.filter(used_at=None)


# --------------------------------------------------------------------------------
# > Admins
# --------------------------------------------------------------------------------
@admin.register(SecurityToken)
class TokenAdmin(CannotAddMixin, CannotEditMixin, admin.ModelAdmin):
    """
    Admin to display the Token model. For security reason:
        Cannot create new entries through the admin. You must use the Token API
        Cannot edit existing entries. All fields will be shown as read only
    """

    # ----------------------------------------
    # Custom Fields
    # ----------------------------------------
    def token_is_expired(self, token):
        """
        Returns the "is_expired" property of our token
        :param Token token: The current Token instance
        :return: The 'is_expired' field value
        :rtype: bool
        """
        return token.is_expired

    token_is_expired.short_description = "Expired"
    token_is_expired.boolean = True

    def token_is_used(self, token):
        """
        Returns the "is_used" property of our token
        :param Token token: The current Token instance
        :return: The 'is_used' field value
        :rtype: bool
        """
        return token.is_used

    token_is_used.short_description = "Used"
    token_is_used.boolean = True

    # ----------------------------------------
    # List view
    # ----------------------------------------
    list_display = [
        "id",
        "created_at",
        "user",
        "type",
        "token_is_expired",
        "token_is_used",
        "is_active_token",
    ]
    list_display_links = ["id", "created_at", "user", "type"]
    list_editable = []
    list_filter = [
        "user",
        "type",
        IsExpiredFilter,
        IsUsedFilter,
        "is_active_token",
    ]
    ordering = ["-id"]
    search_fields = ["type"]
    sortable_fields = [
        "id",
        "created_at",
        "user",
        "type",
    ]

    # ----------------------------------------
    # Detail view
    # ----------------------------------------
    autocomplete_fields = []
    readonly_fields = [
        "id",
        "created_at",
        "updated_at",
        "user",
        "type",
        "expired_at",
        "used_at",
        "is_active_token",
        "is_expired",
        "is_used",
    ]
    radio_fields = {}
    raw_id_fields = []
    fieldsets = [
        ["CORE", {"fields": ["id", "created_at", "updated_at"],},],
        ["INFO", {"fields": ["user", "type", "value", "expired_at", "used_at"],},],
        ["STATUS", {"fields": ["is_active_token", "is_expired", "is_used"],},],
    ]
