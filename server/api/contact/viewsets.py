"""Viewsets for the 'contact' application"""


# Personal
from jklib.django.drf.permissions import IsAdminUser, IsNotAuthenticated
from jklib.django.drf.viewsets import DynamicViewSet

# Local
from .models import Contact


# --------------------------------------------------------------------------------
# > ViewSets
# --------------------------------------------------------------------------------
class ContactViewset(DynamicViewSet):
    """WIP"""

    queryset = Contact.objects.all()

    viewset_permissions = None

    known_actions = {
        "create": {
            "description": "Sends a new contact message",
            "handler": None,
            "permissions": (IsNotAuthenticated,),
        },
        "list": {
            "description": "List all existing contact messages",
            "handler": None,
            "permissions": (IsAdminUser,),
        },
        "retrieve": {
            "description": "Retrieve one specific contact message",
            "handler": None,
            "permissions": (IsAdminUser,),
        },
        "destroy": {
            "description": "Delete one specific contact message",
            "handler": None,
            "permissions": (IsAdminUser,),
        },
    }
