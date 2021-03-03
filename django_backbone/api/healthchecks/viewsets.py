"""Viewsets for the 'healthchecks' app"""


# Personal
from jklib.django.drf.permissions import IsAdminUser
from jklib.django.drf.viewsets import DynamicViewSet

# Local
from .actions import (
    ApiHealthcheckHandler,
    CacheHealthcheckHandler,
    DatabaseHealthcheckHandler,
    MigrationsHealthcheckHandler,
)


# --------------------------------------------------------------------------------
# > ViewSets
# --------------------------------------------------------------------------------
class HealthcheckViewSet(DynamicViewSet):
    """
    Various healthchecks endpoints that can be pinged to make sure services are up and running
    Every call is logged into a logfile
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
