"""Handler for the 'retrieve' action"""

# Personal
from jklib.django.drf.actions import ModelActionHandler, SerializerMode

# Local
from ._shared import RetrieveNetworkRuleSerializer


# --------------------------------------------------------------------------------
# > Handler
# --------------------------------------------------------------------------------
class RetrieveNetworkRuleHandler(ModelActionHandler):
    """Fetches a NetworkRule info"""

    serializer_mode = SerializerMode.UNIQUE
    serializer = RetrieveNetworkRuleSerializer

    def main(self):
        """
        Fetches the NetworkRule instance data
        :return: HTTP 200 response with the instance data
        :rtype: Response
        """
        return self.model_retrieve()
