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
    PerformPasswordResetHandler,
    RequestPasswordResetHandler,
    RetrieveUserHandler,
    SelfUserHandler,
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
            "handler": LoginHandler,
            "permissions": (IsNotAuthenticated,),
            "methods": ["post"],
            "url_path": "login",
            "detail": False,
        },
        "logout": {
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
        'Self' CRUD which automatically targets the user performing the request
        Services for the 'password reset' process
        Services for the 'verification' process
    """

    queryset = User.objects.all()

    known_actions = {
        "create": {"handler": CreateUserHandler, "permissions": (IsNotAuthenticated,),},
        "list": {"handler": ListUserHandler, "permissions": (IsAdminUser,),},
        "retrieve": {"handler": RetrieveUserHandler, "permissions": (IsAdminOrOwner,),},
        "update": {"handler": UpdateUserHandler, "permissions": (IsAdminOrOwner,),},
        "destroy": {"handler": DestroyUserHandler, "permissions": (IsAdminOrOwner,),},
    }

    extra_actions = {
        # ---------- Self crud ----------
        "self": {
            "handler": SelfUserHandler,
            "permissions": (IsAuthenticated,),  # Targets current user
            "methods": ["get", "put", "delete"],
            "url_path": "self",
            "detail": False,
        },
        "update_password": {
            "handler": UpdatePasswordHandler,
            "permissions": (IsAuthenticated,),  # Targets current user
            "methods": ["post"],
            "url_path": "self/update_password",
            "detail": False,
        },
        # ---------- Verification ----------
        "send_verification_email": {
            "handler": SendVerificationEmailHandler,
            "permissions": (IsAuthenticated, IsNotVerified),  # Targets current user
            "methods": ["post"],
            "url_path": "self/send_verification_email",
            "detail": False,
        },
        "verify": {
            "handler": VerifyHandler,
            "permissions": (AllowAny,),
            "methods": ["post"],
            "url_path": "verify",
            "detail": False,
        },
        # ---------- Password reset ----------
        "request_password_reset": {
            "handler": RequestPasswordResetHandler,
            "permissions": (IsNotAuthenticated,),
            "methods": ["post"],
            "url_path": "request_password_reset",
            "detail": False,
        },
        "perform_password_reset": {
            "handler": PerformPasswordResetHandler,
            "permissions": (IsNotAuthenticated,),
            "methods": ["post"],
            "url_path": "perform_password_reset",
            "detail": False,
        },
    }
