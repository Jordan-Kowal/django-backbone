"""Viewsets for the 'core' application"""

# Personal
from jklib.django.drf.permissions import IsAdminUser
from jklib.django.drf.viewsets import DynamicViewSet

# Application
from api.core.models import IpAddress

# Local
from .actions import CreateIpHandler


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
            "description": "Creates a new user",
            "handler": CreateIpHandler,
            "permissions": None,
        }
    }

    extra_actions = {}
