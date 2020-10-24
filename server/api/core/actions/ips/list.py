"""Handler for the 'list' action"""

# Personal
from jklib.django.drf.actions import ModelActionHandler, SerializerMode

# Local
from ._shared import RetrieveIpSerializer


# --------------------------------------------------------------------------------
# > Handler
# --------------------------------------------------------------------------------
class ListIpHandler(ModelActionHandler):
    """Fetches the info of all existing IPs"""

    serializer_mode = SerializerMode.UNIQUE
    serializer = RetrieveIpSerializer

    def main(self):
        """
        Fetches all existing IpAddress instances data
        :return: HTTP 200 response with the instance data
        :rtype: Response
        """
        return self.model_list()
