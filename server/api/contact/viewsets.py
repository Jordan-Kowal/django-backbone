"""Viewsets for the 'contact' application"""

# Django
from rest_framework.permissions import AllowAny

# Personal
from jklib.django.drf.permissions import IsAdminUser
from jklib.django.drf.viewsets import DynamicViewSet

# Local
from .actions import (
    BulkDestroyContactsHandler,
    CreateContactHandler,
    DestroyContactHandler,
    ListContactHandler,
    RetrieveContactHandler,
)
from .models import Contact


# --------------------------------------------------------------------------------
# > ViewSets
# --------------------------------------------------------------------------------
class ContactViewset(DynamicViewSet):
    """
    Viewset mostly for the Contact model
    Due to the nature of this model, there is no update API
    """

    queryset = Contact.objects.all()

    viewset_permissions = None

    known_actions = {
        "create": {
            "description": "Creates and sends a new contact message",
            "handler": CreateContactHandler,
            "permissions": (AllowAny,),
        },
        "list": {
            "description": "List all existing contact messages",
            "handler": ListContactHandler,
            "permissions": (IsAdminUser,),
        },
        "retrieve": {
            "description": "Retrieve one specific contact message",
            "handler": RetrieveContactHandler,
            "permissions": (IsAdminUser,),
        },
        "destroy": {
            "description": "Delete one specific contact message",
            "handler": DestroyContactHandler,
            "permissions": (IsAdminUser,),
        },
    }

    extra_actions = {
        "bulk_destroy": {
            "description": "Deletes several Contact instances at once",
            "handler": BulkDestroyContactsHandler,
            "permissions": (IsAdminUser,),
            "methods": ["delete"],
            "detail": False,
        },
    }
