"""ExtendedUserAdmin"""

# Django
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

# Local
from ..models import Profile


# --------------------------------------------------------------------------------
# > Inlines
# --------------------------------------------------------------------------------
class UserProfileInline(admin.StackedInline):
    """Inline used to import our Profile within the UserAdmin"""

    # ----------------------------------------
    # Setup
    # ----------------------------------------
    model = Profile
    can_delete = False
    fk_name = "user"

    # ----------------------------------------
    # Detail view
    # ----------------------------------------
    autocomplete_fields = []
    readonly_fields = []
    radio_fields = {}
    raw_id_fields = []
    fieldsets = [
        [
            "",
            {
                "fields": [
                    "is_verified",
                ],
            },
        ],
    ]


# --------------------------------------------------------------------------------
# > Admins
# --------------------------------------------------------------------------------
admin.site.unregister(User)


@admin.register(User)
class ExtendedUserAdmin(UserAdmin):
    """Improved UserAdmin with better list view and added the Profile as inline in detail view"""

    # ----------------------------------------
    # Custom Fields
    # ----------------------------------------
    def user_is_verified(self, user):
        """
        Returns the "verified" info from the user profile
        :param User user: The current User instance
        :return: The 'is_verified' field value
        :rtype: bool
        """
        return user.profile.is_verified

    user_is_verified.short_description = "Verified"
    user_is_verified.boolean = True

    # ----------------------------------------
    # List view
    # ----------------------------------------
    list_display = [
        "id",
        "email",
        "last_login",
        "user_is_verified",
        "is_active",
    ]
    list_display_links = ["id", "email", "last_login"]
    list_editable = ["is_active"]
    list_filter = ["is_active", "profile__is_verified"]
    ordering = ["-id"]
    search_fields = ["email"]
    sortable_fields = [
        "id",
        "email",
        "last_login",
        "profile__is_verified",
        "is_active",
    ]

    # ----------------------------------------
    # Detail view
    # ----------------------------------------
    # Given its complexity, we prefer not to change the detail view
    # We simply ADD another inline
    inlines = UserAdmin.inlines + [
        UserProfileInline,
    ]
