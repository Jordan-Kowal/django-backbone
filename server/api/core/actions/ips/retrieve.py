"""Handler for the 'retrieve' action"""

# Personal
from jklib.django.drf.actions import ModelActionHandler, SerializerMode

# Local
from ._shared import RetrieveIpSerializer


# --------------------------------------------------------------------------------
# > Handler
# --------------------------------------------------------------------------------
class RetrieveIpHandler(ModelActionHandler):
    """Fetches an IP info"""

    serializer_mode = SerializerMode.UNIQUE
    serializer = RetrieveIpSerializer

    def main(self):
        """
        Fetches the IpAddress instance data
        :return: HTTP 200 response with the instance data
        :rtype: Response
        """
        return self.model_retrieve()
