"""Handler for the 'update' action"""

# Personal
from jklib.django.drf.actions import ModelActionHandler, SerializerMode

# Local
from ._shared import CreateOrUpdateIpSerializer


# --------------------------------------------------------------------------------
# > Handler
# --------------------------------------------------------------------------------
class UpdateIpHandler(ModelActionHandler):
    """Updates an existing IP"""

    serializer_mode = SerializerMode.UNIQUE
    serializer = CreateOrUpdateIpSerializer

    def main(self):
        """
        Updates the IpAddress model with the provided data
        :return: HTTP 201 response with the IpAddress data
        :rtype: Response
        """
        return self.model_update()
