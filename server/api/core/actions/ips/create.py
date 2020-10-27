"""Handler for the 'create' action"""

# Personal
from jklib.django.drf.actions import ModelActionHandler, SerializerMode

# Local
from ._shared import CreateOrUpdateIpSerializer


# --------------------------------------------------------------------------------
# > Handler
# --------------------------------------------------------------------------------
class CreateIpHandler(ModelActionHandler):
    """Registers a new IP with the provided info"""

    serializer_mode = SerializerMode.UNIQUE
    serializer = CreateOrUpdateIpSerializer

    def main(self):
        """
        Creates the IpAddress model with the provided data
        :return: HTTP 201 response with the IpAddress data
        :rtype: Response
        """
        return self.model_create()
