"""Viewsets for the 'core' application"""

# Personal
from jklib.django.drf.permissions import IsAdminUser
from jklib.django.drf.viewsets import DynamicViewSet

# Application
from api.core.models import IpAddress

# Local
from .actions import CreateIpHandler, DestroyIpHandler, ListIpHandler, RetrieveIpHandler


# --------------------------------------------------------------------------------
# > ViewSets
# --------------------------------------------------------------------------------
class IpViewSet(DynamicViewSet):
    """
    Viewset for the IpAddress models.
    Services can be split into the following categories:
        Classic model CRUD
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
        "destroy": {
            "description": "Deletes an existing IP",
            "handler": DestroyIpHandler,
            "permissions": None,
        },
    }

    extra_actions = {}
