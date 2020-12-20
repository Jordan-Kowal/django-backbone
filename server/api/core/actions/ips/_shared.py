"""
Reusable classes, functions and variables available for all our core ip services
Split into the following categories:
    Status Management
    Serializers
    Representation
    Validators
"""

# Built-in
from datetime import date

# Django
from rest_framework import serializers
from rest_framework.serializers import (
    BooleanField,
    CharField,
    DateField,
    ModelSerializer,
    ValidationError,
)

# Personal
from jklib.django.drf.serializers import NotEmptyModelSerializer, required

# Application
from api.core.models import IpAddress

# --------------------------------------------------------------------------------
# > Status management
# --------------------------------------------------------------------------------
STATUS_TO_ENUM = {
    1: IpAddress.IpStatus.NONE,
    2: IpAddress.IpStatus.WHITELISTED,
    3: IpAddress.IpStatus.BLACKLISTED,
    "NONE": IpAddress.IpStatus.NONE,
    "WHITELISTED": IpAddress.IpStatus.WHITELISTED,
    "BLACKLISTED": IpAddress.IpStatus.BLACKLISTED,
}

STATUS_CHOICES = list(STATUS_TO_ENUM.keys())


# --------------------------------------------------------------------------------
# > Serializers
# --------------------------------------------------------------------------------
class BlacklistOrWhitelistExistingIpSerializer(ModelSerializer):
    """
    Serializer to blacklist or whitelist an existing IP
    The choice between blacklist/whitelist should happen in the ActionHandler
    """

    # Overridden to pass default values and make them truly optional
    expires_on = DateField(default=None, allow_null=True)
    comment = CharField(max_length=IpAddress.COMMENT_MAX_LENGTH, default="")
    override = BooleanField(default=False)

    # ----------------------------------------
    # Behavior
    # ----------------------------------------
    class Meta:
        """Meta class to setup the serializer"""

        model = IpAddress
        fields = [
            "expires_on",
            "comment",
            "override",
        ]

    # ----------------------------------------
    # Validation
    # ----------------------------------------
    @staticmethod
    def validate_expires_on(expiration_date):
        """
        If a date is provided, check that it is not in the past
        :param date expiration_date: The provided datetime value
        :return: The untouched expiration date
        :rtype: date
        """
        if expiration_date:
            expiration_date = validate_expires_on(expiration_date)
        return expiration_date


class BlacklistOrWhitelistNewIpSerializer(NotEmptyModelSerializer):
    """
    Serializer to create and blacklist/whitelist an IpAddress instance
    Similar to the CreateOrUpdateIpSerializer but with fewer fields
    The choice between blacklist/whitelist should happen in the ActionHandler
    """

    # ----------------------------------------
    # Behavior
    # ----------------------------------------
    class Meta:
        """Meta class to setup the serializer"""

        model = IpAddress
        fields = [
            "ip",
            "expires_on",
            "comment",
        ]

    def to_representation(self, ip_address):
        """
        Returns the formatted IpAddress data
        :param IpAddress ip_address: The created or updated IpAddress
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
        If a date is provided, check that it is not in the past
        :param date expiration_date: The provided datetime value
        :return: The untouched expiration date
        :rtype: date
        """
        if expiration_date:
            expiration_date = validate_expires_on(expiration_date)
        return expiration_date


class CreateOrUpdateIpSerializer(NotEmptyModelSerializer):
    """
    Serializer to create or update an IpAddress instance
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

    def to_representation(self, ip_address):
        """
        Returns the formatted IpAddress data
        :param IpAddress ip_address: The created or updated IpAddress
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
        If a date is provided, check that it is not in the past
        :param date expiration_date: The provided datetime value
        :return: The untouched expiration date
        :rtype: date
        """
        if expiration_date:
            expiration_date = validate_expires_on(expiration_date)
        return expiration_date

    @staticmethod
    def validate_status(status):
        """
        Converts the status to enum and checks if it is a valid option
        :param status: The provided status for the IpAddress
        :type status: str or int
        :return: The status converted to its enum integer value
        :rtype: int
        """
        return validate_status(status)


class RetrieveIpSerializer(ModelSerializer):
    """Model serializer to fetch our IpAddress data"""

    class Meta:
        """Meta class to setup the serializer"""

        model = IpAddress

    def to_representation(self, ip_address):
        """
        Returns the formatted IpAddress data
        :param IpAddress ip_address: The created IpAddress
        :return: Dict with our formatted IpAddress data
        :rtype: dict
        """
        return ip_address_representation(ip_address)


# --------------------------------------------------------------------------------
# > Representation
# --------------------------------------------------------------------------------
def ip_address_representation(ip_address):
    """
    Formats an IpAddress model into a dict
    :param IpAddress ip_address: The IpAddress model to return
    :return: Dict of our IpAddress data
    :rtype: dict
    """
    return {
        "id": ip_address.id,
        "ip": ip_address.ip,
        "status": ip_address.status,
        "expires_on": ip_address.expires_on,
        "active": ip_address.active,
        "comment": ip_address.comment,
    }


# --------------------------------------------------------------------------------
# > Validators
# --------------------------------------------------------------------------------
def validate_expires_on(expiration_date):
    """
    Checks that the expiration date is not in the past
    :param date expiration_date: The provided datetime value
    :raises ValidationError: When the date is in the past
    :return: The untouched expiration date
    :rtype: date
    """
    if expiration_date < date.today():
        raise ValidationError("Expiration date cannot be in the past")
    return expiration_date


def validate_status(status):
    """
    Converts the status from int/str to a valid enum
    :param status: The provided status for the IpAddress
    :type status: str or int
    :raises ValidationError: If the status value is unknown
    :return: The status converted to its enum integer value
    :rtype: int
    """
    status_enum = STATUS_TO_ENUM.get(status, None)
    if status_enum is None:
        raise ValidationError("Provided 'status' is invalid")
    return status_enum
