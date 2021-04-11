"""Admins for the 'contact' app"""


# Django
from django.contrib import admin

# Local
from .models import Contact


# --------------------------------------------------------------------------------
# > Admins
# --------------------------------------------------------------------------------
@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    """Custom admin to display the Contact model"""

    # ----------------------------------------
    # Actions
    # ----------------------------------------
    def has_add_permission(self, request, obj=None):
        """Prevents adding a new entry through the django admin interface"""
        return False

    # ----------------------------------------
    # List view
    # ----------------------------------------
    list_display = [
        "id",
        "created_at",
        "ip",
        "name",
        "email",
        "subject",
    ]
    list_display_links = [
        "id",
        "created_at",
        "ip",
        "name",
        "email",
        "subject",
    ]
    list_editable = []
    list_filter = []
    ordering = ["-id"]
    search_fields = [
        "ip",
        "name",
        "email",
        "subject",
    ]
    sortable_fields = [
        "id",
        "created_at",
        "ip",
        "name",
        "email",
        "subject",
    ]

    # ----------------------------------------
    # Detail view
    # ----------------------------------------
    autocomplete_fields = []
    readonly_fields = [
        "id",
        "created_at",
        "ip",
        "name",
        "email",
        "subject",
        "body",
    ]
    radio_fields = {}
    raw_id_fields = []
    fieldsets = [
        ["Informations Structurelles", {"fields": ["id", "created_at",],},],
        ["Contenu", {"fields": ["ip", "name", "email", "subject", "body",],},],
    ]
