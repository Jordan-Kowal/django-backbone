"""Handler for the 'retrieve' action"""

# Django
from rest_framework.serializers import ModelSerializer

# Personal
from jklib.django.drf.actions import ModelActionHandler, SerializerMode

# Application
from api.core.models import IpAddress

# Local
from ._shared import ip_address_representation


# --------------------------------------------------------------------------------
# > Serializers
# --------------------------------------------------------------------------------
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
# > Handler
# --------------------------------------------------------------------------------
class RetrieveIpHandler(ModelActionHandler):
    """Registers a new IP with the provided info"""

    serializer_mode = SerializerMode.UNIQUE
    serializer = RetrieveIpSerializer

    def main(self):
        """
        Fetches the IpAddress instance data
        :return: HTTP 200 response with the user data
        :rtype: Response
        """
        return self.model_retrieve()
