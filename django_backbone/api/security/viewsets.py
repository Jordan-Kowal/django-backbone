"""Viewsets for the 'security' app"""

# Personal
from jklib.django.drf.permissions import IsAdminUser
from jklib.django.drf.viewsets import DynamicViewSet

# Local
from .actions import (
    BlacklistNetworkRuleHandler,
    BulkDestroyNetworkRulesHandler,
    ClearAllNetworkRulesHandler,
    ClearNetworkRuleHandler,
    CreateNetworkRuleHandler,
    DestroyNetworkRuleHandler,
    ListNetworkRulesHandler,
    NewBlacklistNetworkRuleHandler,
    NewWhitelistNetworkRuleHandler,
    RetrieveNetworkRuleHandler,
    UpdateNetworkRuleHandler,
    WhitelistNetworkRuleHandler,
)
from .models import NetworkRule


# --------------------------------------------------------------------------------
# > ViewSets
# --------------------------------------------------------------------------------
class NetworkRuleViewSet(DynamicViewSet):
    """
    Viewset for the NetworkRule models.
    Services can be split into the following categories:
        Classic model CRUD
        Additional CRUD
        IP blacklisting
        IP whitelisting
        IP clearing
    """

    queryset = NetworkRule.objects.all()

    viewset_permissions = (IsAdminUser,)

    known_actions = {
        "create": {
            "description": "Registers a new network rule",
            "handler": CreateNetworkRuleHandler,
            "permissions": None,
        },
        "list": {
            "description": "List all existing network rules",
            "handler": ListNetworkRulesHandler,
            "permissions": None,
        },
        "retrieve": {
            "description": "Fetches an existing network rule",
            "handler": RetrieveNetworkRuleHandler,
            "permissions": None,
        },
        "update": {
            "description": "Updates an existing network rule",
            "handler": UpdateNetworkRuleHandler,
            "permissions": None,
        },
        "destroy": {
            "description": "Deletes an existing network rule",
            "handler": DestroyNetworkRuleHandler,
            "permissions": None,
        },
    }

    extra_actions = {
        # Additional CRUD
        "bulk_destroy": {
            "description": "Deletes several network rules instances at once",
            "handler": BulkDestroyNetworkRulesHandler,
            "permissions": None,
            "methods": ["delete"],
            "detail": False,
        },
        # Blacklist
        "blacklist_new": {
            "description": "Creates a network rule to blacklist an IP",
            "handler": NewBlacklistNetworkRuleHandler,
            "permissions": None,
            "methods": ["post"],
            "detail": False,
            "url_path": "blacklist",
        },
        "blacklist_existing": {
            "description": "Updates a network rule to blacklist an IP",
            "handler": BlacklistNetworkRuleHandler,
            "permissions": None,
            "methods": ["post"],
            "detail": True,
            "url_path": "blacklist",
        },
        # Whitelist
        "whitelist_new": {
            "description": "Creates a network rule to whitelist an IP",
            "handler": NewWhitelistNetworkRuleHandler,
            "permissions": None,
            "methods": ["post"],
            "detail": False,
            "url_path": "whitelist",
        },
        "whitelist_existing": {
            "description": "Updates a network rule to whitelist an IP",
            "handler": WhitelistNetworkRuleHandler,
            "permissions": None,
            "methods": ["post"],
            "detail": True,
            "url_path": "whitelist",
        },
        # Clear
        "clear": {
            "description": "Clears an existing network rule",
            "handler": ClearNetworkRuleHandler,
            "permissions": None,
            "methods": ["post"],
            "detail": True,
        },
        "clear_all": {
            "description": "Clears all existing network rules (can be restricted to a specific status)",
            "handler": ClearAllNetworkRulesHandler,
            "permissions": None,
            "methods": ["post"],
            "detail": False,
        },
    }
