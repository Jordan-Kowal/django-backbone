"""Handler for the 'create' action"""

# Personal
from jklib.django.drf.actions import ModelActionHandler, SerializerMode

# Local
from ._shared import CreateOrUpdateNetworkRuleSerializer


# --------------------------------------------------------------------------------
# > Handler
# --------------------------------------------------------------------------------
class CreateNetworkRuleHandler(ModelActionHandler):
    """Registers a new NetworkRule with the provided info"""

    serializer_mode = SerializerMode.UNIQUE
    serializer = CreateOrUpdateNetworkRuleSerializer

    def main(self):
        """
        Creates the NetworkRule model with the provided data
        :return: HTTP 201 response with the NetworkRule data
        :rtype: Response
        """
        return self.model_create()
