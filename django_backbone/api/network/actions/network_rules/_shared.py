"""
Reusable classes, functions and variables available for all our network rule services
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

# Local
from ...models import NetworkRule

# --------------------------------------------------------------------------------
# > Status management
# --------------------------------------------------------------------------------
STATUS_TO_ENUM = {
    1: NetworkRule.Status.NONE,
    2: NetworkRule.Status.WHITELISTED,
    3: NetworkRule.Status.BLACKLISTED,
    "NONE": NetworkRule.Status.NONE,
    "WHITELISTED": NetworkRule.Status.WHITELISTED,
    "BLACKLISTED": NetworkRule.Status.BLACKLISTED,
}

STATUS_CHOICES = list(STATUS_TO_ENUM.keys())


# --------------------------------------------------------------------------------
# > Serializers
# --------------------------------------------------------------------------------
class ActivateNetworkRuleSerializer(ModelSerializer):
    """
    Serializer to blacklist or whitelist an existing rule
    The choice between blacklist/whitelist should happen in the ActionHandler
    """

    # Overridden to pass default values and make them truly optional
    expires_on = DateField(default=None, allow_null=True)
    comment = CharField(max_length=NetworkRule.COMMENT_MAX_LENGTH, default="")
    override = BooleanField(default=False)

    # ----------------------------------------
    # Behavior
    # ----------------------------------------
    class Meta:
        """Meta class to setup the serializer"""

        model = NetworkRule
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


class CreateActiveNetworkRuleSerializer(NotEmptyModelSerializer):
    """
    Serializer to create and blacklist/whitelist a NetworkRule instance
    Similar to the CreateOrUpdateNetworkRuleSerializer but with fewer fields
    The choice between blacklist/whitelist should happen in the ActionHandler
    """

    # ----------------------------------------
    # Behavior
    # ----------------------------------------
    class Meta:
        """Meta class to setup the serializer"""

        model = NetworkRule
        fields = [
            "ip",
            "expires_on",
            "comment",
        ]

    def to_representation(self, network_rule):
        """
        Returns the formatted NetworkRule data
        :param NetworkRule network_rule: The created or updated NetworkRule
        :return: Dict with our formatted NetworkRule data
        :rtype: dict
        """
        return network_rule_representation(network_rule)

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


class CreateOrUpdateNetworkRuleSerializer(NotEmptyModelSerializer):
    """
    Serializer to create or update a NetworkRule instance
    The 'status' field accepts either string or integer matching our enum
    """

    status = serializers.ChoiceField(choices=STATUS_CHOICES, **required())

    # ----------------------------------------
    # Behavior
    # ----------------------------------------
    class Meta:
        """Meta class to setup the serializer"""

        model = NetworkRule
        fields = [
            "ip",
            "status",  # overridden
            "expires_on",
            "active",
            "comment",
        ]

    def to_representation(self, network_rule):
        """
        Returns the formatted NetworkRule data
        :param NetworkRule network_rule: The created or updated NetworkRule
        :return: Dict with our formatted NetworkRule data
        :rtype: dict
        """
        return network_rule_representation(network_rule)

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
        :param status: The provided status for the NetworkRule
        :type status: str or int
        :return: The status converted to its enum integer value
        :rtype: int
        """
        return validate_status(status)


class RetrieveNetworkRuleSerializer(ModelSerializer):
    """Model serializer to fetch our NetworkRule data"""

    class Meta:
        """Meta class to setup the serializer"""

        model = NetworkRule

    def to_representation(self, network_rule):
        """
        Returns the formatted NetworkRule data
        :param NetworkRule network_rule: The created NetworkRule
        :return: Dict with our formatted NetworkRule data
        :rtype: dict
        """
        return network_rule_representation(network_rule)


# --------------------------------------------------------------------------------
# > Representation
# --------------------------------------------------------------------------------
def network_rule_representation(network_rule):
    """
    Formats a NetworkRule model into a dict
    :param NetworkRule network_rule: The NetworkRule model to return
    :return: Dict of our NetworkRule data
    :rtype: dict
    """
    return {
        "id": network_rule.id,
        "ip": network_rule.ip,
        "status": network_rule.status,
        "expires_on": network_rule.expires_on,
        "active": network_rule.active,
        "comment": network_rule.comment,
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
    :param status: The provided status for the NetworkRule
    :type status: str or int
    :raises ValidationError: If the status value is unknown
    :return: The status converted to its enum integer value
    :rtype: int
    """
    status_enum = STATUS_TO_ENUM.get(status, None)
    if status_enum is None:
        raise ValidationError("Provided 'status' is invalid")
    return status_enum
