"""Viewsets for the 'core' application"""

# Personal
from jklib.django.drf.permissions import IsAdminUser
from jklib.django.drf.viewsets import DynamicViewSet

# Application
from api.core.models import IpAddress

# Local
from .actions import (
    BlacklistExistingIpHandler,
    BlacklistNewIpHandler,
    ClearAllIpsHandler,
    ClearIpHandler,
    CreateIpHandler,
    DestroyIpHandler,
    ListIpHandler,
    RetrieveIpHandler,
    UpdateIpHandler,
    WhitelistExistingIpHandler,
    WhitelistNewIpHandler,
)


# --------------------------------------------------------------------------------
# > ViewSets
# --------------------------------------------------------------------------------
class IpViewSet(DynamicViewSet):
    """
    Viewset for the IpAddress models.
    Services can be split into the following categories:
        Classic model CRUD
        IP blacklisting
        IP whitelisting
        IP clearing
    """

    queryset = IpAddress.objects.all()

    viewset_permissions = (IsAdminUser,)

    known_actions = {
        "create": {
            "description": "Registers a new IP",
            "handler": CreateIpHandler,
            "permissions": None,
        },
        "list": {
            "description": "List all existing IPs",
            "handler": ListIpHandler,
            "permissions": None,
        },
        "retrieve": {
            "description": "Fetches an existing IP",
            "handler": RetrieveIpHandler,
            "permissions": None,
        },
        "update": {
            "description": "Updates an existing IP",
            "handler": UpdateIpHandler,
            "permissions": None,
        },
        "destroy": {
            "description": "Deletes an existing IP",
            "handler": DestroyIpHandler,
            "permissions": None,
        },
    }

    extra_actions = {
        # Blacklist
        "blacklist_new": {
            "description": "Creates and blacklists an IP",
            "handler": BlacklistNewIpHandler,
            "permissions": None,
            "methods": ["post"],
            "url_path": "blacklist",
            "detail": False,
        },
        "blacklist_existing": {
            "description": "Blacklists an existing IP",
            "handler": BlacklistExistingIpHandler,
            "permissions": None,
            "methods": ["post"],
            "url_path": "blacklist",
            "detail": True,
        },
        # Whitelist
        "whitelist_new": {
            "description": "Creates and whitelists an IP",
            "handler": WhitelistNewIpHandler,
            "permissions": None,
            "methods": ["post"],
            "url_path": "whitelist",
            "detail": False,
        },
        "whitelist_existing": {
            "description": "Whitelists an existing IP",
            "handler": WhitelistExistingIpHandler,
            "permissions": None,
            "methods": ["post"],
            "url_path": "whitelist",
            "detail": True,
        },
        # Clear
        "clear": {
            "description": "Clears an existing IP",
            "handler": ClearIpHandler,
            "permissions": None,
            "methods": ["post"],
            "url_path": "clear",
            "detail": True,
        },
        "clear_all": {
            "description": "Clears all existing IPs (can be restricted to a specific status)",
            "handler": ClearAllIpsHandler,
            "permissions": None,
            "methods": ["post"],
            "url_path": "clear_all",
            "detail": False,
        },
    }
