"""Handler for the 'blacklist_existing' action"""

# Django
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_409_CONFLICT

# Personal
from jklib.django.drf.actions import ModelActionHandler, SerializerMode

# Local
from ._shared import BlacklistOrWhitelistExistingIpSerializer, ip_address_representation


# --------------------------------------------------------------------------------
# > Handler
# --------------------------------------------------------------------------------
class BlacklistExistingIpHandler(ModelActionHandler):
    """
    Blacklists an existing IP
    Missing fields will be defaulted and will override the instance current value
    """

    serializer_mode = SerializerMode.UNIQUE
    serializer = BlacklistOrWhitelistExistingIpSerializer

    def main(self):
        """
        Blacklists an existing IpAddress instance
        :return: HTTP 200 response with the IpAddress data
        :rtype: Response
        """
        instance = self.viewset.get_object()
        serializer = self.get_valid_serializer(instance, data=self.data)
        payload = {
            "end_date": serializer.validated_data.get("expires_on", None),
            "comment": serializer.validated_data.get("comment", None),
            "override": serializer.validated_data.get("override", False),
        }
        # Override condition
        if instance.is_whitelisted and not payload["override"]:
            return Response(None, status=HTTP_409_CONFLICT)
        # Blacklists the IP
        instance.blacklist(**payload)
        data = ip_address_representation(instance)
        return Response(data, status=HTTP_200_OK)
