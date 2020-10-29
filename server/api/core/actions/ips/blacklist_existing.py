"""Handler for the 'blacklist_existing' action"""

# Django
from rest_framework.response import Response
from rest_framework.serializers import (
    BooleanField,
    CharField,
    DateField,
    ModelSerializer,
    ValidationError,
)
from rest_framework.status import HTTP_200_OK

# Personal
from jklib.django.drf.actions import ModelActionHandler, SerializerMode

# Local
from ...models import IpAddress
from ._shared import ip_address_representation, validate_expires_on


# --------------------------------------------------------------------------------
# > Serializer
# --------------------------------------------------------------------------------
class BlacklistExistingIpSerializer(ModelSerializer):
    """Serializer to blacklist an existing IP"""

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

    def update(self, instance, validated_data):
        """
        Blacklists the instance with the given parameters
        :param IpAddress instance: The current IpAddress instance
        :param dict validated_data: The validated request data
        :return: The updated instance
        :rtype: IpAddress
        """
        payload = {
            "end_date": validated_data.get("expires_on", None),
            "comment": validated_data.get("comment", None),
            "override": validated_data.get("override", False),
        }
        instance.blacklist(**payload)
        return instance

    def to_representation(self, ip_address):
        """
        Returns the formatted IpAddress data
        :param IpAddress ip_address: The updated IpAddress
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

    def validate_override(self, override):
        """
        Raises an error if you try to blacklist a whitelisted IP without override
        :param bool override: Whether to bypass the validation error
        :return: The unchanged parameter
        :rtype: bool
        """
        if self.instance.is_whitelisted and not override:
            raise ValidationError(
                "Cannot blacklist a whitelisted IP without 'override' set to True"
            )
        return override


# --------------------------------------------------------------------------------
# > Handler
# --------------------------------------------------------------------------------
class BlacklistExistingIpHandler(ModelActionHandler):
    """
    Blacklists an existing IP
    Missing fields will be defaulted and will override the instance current value
    """

    serializer_mode = SerializerMode.UNIQUE
    serializer = BlacklistExistingIpSerializer

    def main(self):
        """
        Blacklists an existing IpAddress instance
        :return: HTTP 200 response with the IpAddress data
        :rtype: Response
        """
        instance = self.viewset.get_object()
        serializer = self.get_valid_serializer(instance, data=self.data)
        serializer.save()
        return Response(serializer.data, status=HTTP_200_OK)
