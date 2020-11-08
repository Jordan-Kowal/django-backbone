"""Handler for the 'whitelist_new' action"""

# Django
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED

# Personal
from jklib.django.drf.actions import ActionHandler, SerializerMode

# Local
from ._shared import BlacklistOrWhitelistNewIpSerializer, ip_address_representation


# --------------------------------------------------------------------------------
# > Handler
# --------------------------------------------------------------------------------
class WhitelistNewIpHandler(ActionHandler):
    """Creates and whitelists a new IP"""

    serializer_mode = SerializerMode.UNIQUE
    serializer = BlacklistOrWhitelistNewIpSerializer

    def main(self):
        """
        Creates and whitelists the IpAddress model with the provided data
        :return: HTTP 201 response with the IpAddress data
        :rtype: Response
        """
        serializer = self.get_valid_serializer(data=self.data)
        instance = serializer.save()
        payload = {
            "end_date": serializer.validated_data.get("expires_on", None),
            "comment": serializer.validated_data.get("comment", None),
            "override": True,
        }
        instance.whitelist(**payload)
        data = ip_address_representation(instance)
        return Response(data, status=HTTP_201_CREATED)
