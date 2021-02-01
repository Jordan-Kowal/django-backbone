"""Viewsets for the 'core' application"""

# Personal
from jklib.django.drf.permissions import IsAdminUser
from jklib.django.drf.viewsets import DynamicViewSet

# Application
from api.core.models import NetworkRule

# Local
from .actions import (
    ApiHealthcheckHandler,
    BlacklistNetworkRuleHandler,
    BulkDestroyNetworkRulesHandler,
    CacheHealthcheckHandler,
    ClearAllNetworkRulesHandler,
    ClearNetworkRuleHandler,
    CreateNetworkRuleHandler,
    DatabaseHealthcheckHandler,
    DestroyNetworkRuleHandler,
    ListNetworkRulesHandler,
    MigrationsHealthcheckHandler,
    NewBlacklistNetworkRuleHandler,
    NewWhitelistNetworkRuleHandler,
    RetrieveNetworkRuleHandler,
    UpdateNetworkRuleHandler,
    WhitelistNetworkRuleHandler,
)


# --------------------------------------------------------------------------------
# > ViewSets
# --------------------------------------------------------------------------------
class HealthcheckViewSet(DynamicViewSet):
    """
    Various healthcheck endpoints that can be pinged to make sure services are up and running
    Every call will be logged into the HealthcheckLog model
    """

    viewset_permissions = (IsAdminUser,)

    extra_actions = {
        "api": {
            "description": "Checks if the API is up and running",
            "handler": ApiHealthcheckHandler,
            "permissions": None,
            "methods": ["get"],
            "detail": False,
        },
        "cache": {
            "description": "Checks if the cache is working",
            "handler": CacheHealthcheckHandler,
            "permissions": None,
            "methods": ["get"],
            "detail": False,
        },
        "database": {
            "description": "Checks if the database is up and working",
            "handler": DatabaseHealthcheckHandler,
            "permissions": None,
            "methods": ["get"],
            "detail": False,
        },
        "migrations": {
            "description": "Checks if all migrations have been run",
            "handler": MigrationsHealthcheckHandler,
            "permissions": None,
            "methods": ["get"],
            "detail": False,
        },
    }


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
