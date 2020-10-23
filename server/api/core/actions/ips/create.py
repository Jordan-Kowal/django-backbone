"""Handler for the 'create' action"""

# Django
from rest_framework import serializers

# Personal
from jklib.django.drf.actions import ModelActionHandler, SerializerMode
from jklib.django.drf.serializers import NotEmptyModelSerializer, required

# Application
from api.core.models import IpAddress

# Local
from ._shared import (
    STATUS_CHOICES,
    ip_address_representation,
    validate_expires_on,
    validate_status,
)


# --------------------------------------------------------------------------------
# > Serializers
# --------------------------------------------------------------------------------
class CreateIpSerializer(NotEmptyModelSerializer):
    """
    Serializer to create a new IpAddress instance
    The 'status' field accepts either string or integer matching our enum
    """

    status = serializers.ChoiceField(choices=STATUS_CHOICES, **required())

    # ----------------------------------------
    # Behavior
    # ----------------------------------------
    class Meta:
        """Meta class to setup the serializer"""

        model = IpAddress
        fields = [
            "ip",
            "status",  # overridden
            "expires_on",
            "active",
            "comment",
        ]
        extra_kwargs = {
            "expires_on": {"required": True, "allow_null": False},
        }

    def to_representation(self, ip_address):
        """
        Returns the formatted IpAddress data
        :param IpAddress ip_address: The created IpAddress
        :return: Dict with our formatted IpAddress data
        :rtype: dict
        """
        return ip_address_representation(ip_address)

    # ----------------------------------------
    # Validation
    # ----------------------------------------
    @staticmethod
    def validate_expires_on(expiration_date):
        """
        Checks the expiration date is not in the future
        :param date expiration_date: The provided datetime value
        :return: The untouched expiration date
        :rtype: date
        """
        return validate_expires_on(expiration_date)

    @staticmethod
    def validate_status(status):
        """
        Converts the status to integer and checks if it is a valid option
        :param status: The provided status for the IpAddress
        :type status: str or int
        :return: The status converted to its enum integer value
        :rtype: int
        """
        return validate_status(status)


# --------------------------------------------------------------------------------
# > Handler
# --------------------------------------------------------------------------------
class CreateIpHandler(ModelActionHandler):
    """WIP"""

    serializer_mode = SerializerMode.UNIQUE
    serializer = CreateIpSerializer

    def main(self):
        """
        Creates the IpAddress model with the provided data
        :return: HTTP 201 response with the IpAddress data
        :rtype: Response
        """
        return self.model_create()
