"""
Description:
    Contains serializers for our application
Serializers:
    ContactSerializer: Serializer for creating/posting a new Contact entry
"""


# Personal
from jklib.django.drf.serializers import NotEmptyModelSerializer

# Local
from .models import Contact


# --------------------------------------------------------------------------------
# > Serializers
# --------------------------------------------------------------------------------
class ContactSerializer(NotEmptyModelSerializer):
    """
    Serializer for creating/posting a new Contact entry
    The user IP address must be added to the serializer's validated data, in the view
    """

    # ----------------------------------------
    # Meta, create, update
    # ----------------------------------------
    class Meta:
        """Meta class to setup the serializer"""

        model = Contact
        fields = [
            "name",
            "company",
            "email",
            "subject",
            "message",
        ]
