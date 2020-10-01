"""Viewsets for the 'users' application"""

# Django
from django.contrib.auth.models import User

# Personal
from jklib.django.drf.permissions import (
    AllowAny,
    IsAdminOrOwner,
    IsAdminUser,
    IsAuthenticated,
    IsNotAuthenticated,
    IsNotVerified,
    IsObjectOwner,
)
from jklib.django.drf.viewsets import DynamicViewSet

# Local
from .actions import (
    CreateUserHandler,
    DestroyUserHandler,
    ListUserHandler,
    LoginHandler,
    LogoutHandler,
    OverridePasswordHandler,
    PerformPasswordResetHandler,
    RequestPasswordResetHandler,
    RetrieveUserHandler,
    SendVerificationEmailHandler,
    UpdatePasswordHandler,
    UpdateUserHandler,
    VerifyHandler,
)


# --------------------------------------------------------------------------------
# > ViewSets
# --------------------------------------------------------------------------------
class AuthViewSet(DynamicViewSet):
    """Endpoints related to auth management"""

    known_actions = {}

    extra_actions = {
        "login": {
            "description": "Logs in using basic authentication",
            "handler": LoginHandler,
            "permissions": (IsNotAuthenticated,),
            "methods": ["post"],
            "url_path": "login",
            "detail": False,
        },
        "logout": {
            "description": "Disconnects the current user/browser",
            "handler": LogoutHandler,
            "permissions": (IsAuthenticated,),
            "methods": ["post"],
            "url_path": "logout",
            "detail": False,
        },
    }


class UserViewSet(DynamicViewSet):
    """
    Viewset for the User models.
    Services can be split into the following categories:
        Classic model CRUD
        Services for the 'password reset' process
        Services for the 'verification' process
    """

    queryset = User.objects.all()

    known_actions = {
        "create": {
            "description": "Creates a new user",
            "handler": CreateUserHandler,
            "permissions": (IsNotAuthenticated,),
        },
        "list": {
            "description": "List existing users, only accessible to admins",
            "handler": ListUserHandler,
            "permissions": (IsAdminUser,),
        },
        "retrieve": {
            "description": "Retrieve one specific user",
            "handler": RetrieveUserHandler,
            "permissions": (IsAdminOrOwner,),
        },
        "update": {
            "description": "Update one specific users. Admin can update more fields",
            "handler": UpdateUserHandler,
            "permissions": (IsAdminOrOwner,),
        },
        "destroy": {
            "description": "Delete one specific user",
            "handler": DestroyUserHandler,
            "permissions": (IsAdminOrOwner,),
        },
    }

    extra_actions = {
        # ---------- Additional crud ----------
        "update_password": {
            "description": "Update your password by providing the existing one",
            "handler": UpdatePasswordHandler,
            "permissions": (IsObjectOwner,),
            "methods": ["post"],
            "url_path": "update_password",
            "detail": True,
        },
        "override_password": {
            "description": "Allows an admin to override a user's password",
            "handler": OverridePasswordHandler,
            "permissions": (IsAdminUser,),
            "methods": ["post"],
            "url_path": "override_password",
            "detail": True,
        },
        # ---------- Verification ----------
        "send_verification_email": {
            "description": "Sends a verification email to a specific user",
            "handler": SendVerificationEmailHandler,
            "permissions": (IsAdminOrOwner, IsNotVerified),
            "methods": ["post"],
            "url_path": "send_verification_email",
            "detail": True,
        },
        "verify": {
            "description": "Uses a token to 'verify' a user email address",
            "handler": VerifyHandler,
            "permissions": (AllowAny,),
            "methods": ["post"],
            "url_path": "verify",
            "detail": False,
        },
        # ---------- Password reset ----------
        "request_password_reset": {
            "description": "Ask for a password reset link by providing an email address",
            "handler": RequestPasswordResetHandler,
            "permissions": (IsNotAuthenticated,),
            "methods": ["post"],
            "url_path": "request_password_reset",
            "detail": False,
        },
        "perform_password_reset": {
            "description": "Update your password using a security token",
            "handler": PerformPasswordResetHandler,
            "permissions": (IsNotAuthenticated,),
            "methods": ["post"],
            "url_path": "perform_password_reset",
            "detail": False,
        },
    }
