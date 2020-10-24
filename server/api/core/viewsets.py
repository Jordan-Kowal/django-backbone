"""Viewsets for the 'core' application"""

# Personal
from jklib.django.drf.permissions import IsAdminUser
from jklib.django.drf.viewsets import DynamicViewSet

# Application
from api.core.models import IpAddress

# Local
from .actions import CreateIpHandler, RetrieveIpHandler


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
        "retrieve": {
            "description": "Fetches an existing IP",
            "handler": RetrieveIpHandler,
            "permissions": None,
        },
    }

    extra_actions = {}
