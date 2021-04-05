"""Serializers for the 'security' app"""

# Built-in
from datetime import date

# Django
from rest_framework.fields import ChoiceField
from rest_framework.serializers import BooleanField, ModelSerializer, ValidationError

# Personal
from jklib.django.drf.serializers import ImprovedSerializer, optional, required

# Local
from .models import NetworkRule


# --------------------------------------------------------------------------------
# > Serializers
# --------------------------------------------------------------------------------
class NetworkRuleSerializer(ModelSerializer):
    """Basic serializer for NetworkRules"""

    class Meta:
        model = NetworkRule
        fields = [
            "id",
            "ip",
            "status",
            "expires_on",
            "active",
            "comment",
        ]
        read_only_fields = ["id"]

    @staticmethod
    def validate_expires_on(expiration_date):
        """
        If a date is provided, check that it is not in the past
        :param date expiration_date: The provided datetime value
        :raise ValidationError: If the expiration date is in the past
        :return: The untouched expiration date
        :rtype: date
        """
        if expiration_date:
            if expiration_date < date.today():
                raise ValidationError("Expiration date cannot be in the past")
        return expiration_date


class _ActivateNetworkRuleBaseSerializer(NetworkRuleSerializer):
    """Base serializer for activating a NetworkRule"""

    class Meta(NetworkRuleSerializer.Meta):
        fields = ["expires_on", "comment", "status"]
        extra_kwargs = {"status": {**required()}}

    def to_representation(self, network_rule):
        """
        Uses the NetworkRuleSerializer data output
        :param NetworkRule network_rule: The current instance
        :return: The entire NetworkRule data
        :rtype: dict
        """
        return NetworkRuleSerializer(network_rule).data

    @staticmethod
    def validate_status(status):
        """
        Status must be BLACKLISTED or WHITELISTED
        :param int status: Must match the BLACKLISTED or WHITELISTED enum
        :raise ValidationError: If status is not BLACKLISTED or WHITELISTED
        :return: The unchanged expiration date
        :rtype: date
        """
        if status not in {
            NetworkRule.Status.BLACKLISTED,
            NetworkRule.Status.WHITELISTED,
        }:
            raise ValidationError("Status must be BLACKLISTED or WHITELISTED")
        return status


class ActivateNewNetworkRuleSerializer(_ActivateNetworkRuleBaseSerializer):
    """Serializer to create a new blacklisted or whitelisted NetworkRule"""

    class Meta(_ActivateNetworkRuleBaseSerializer.Meta):
        fields = _ActivateNetworkRuleBaseSerializer.Meta.fields + ["ip"]


class ActivateNetworkRuleSerializer(_ActivateNetworkRuleBaseSerializer):
    """Serializer to blacklist or whitelist an existing NetworkRule"""

    override = BooleanField(default=False)

    class Meta(_ActivateNetworkRuleBaseSerializer.Meta):
        fields = _ActivateNetworkRuleBaseSerializer.Meta.fields + ["override"]


class StatusSerializer(ImprovedSerializer):
    """Serializer for a simple NetworkRule.Status"""

    status = ChoiceField(choices=NetworkRule.Status, **optional())

    class Meta(NetworkRuleSerializer.Meta):
        fields = ["status"]
