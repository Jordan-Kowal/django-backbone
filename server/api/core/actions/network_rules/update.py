"""Handler for the 'update' action"""

# Personal
from jklib.django.drf.actions import ModelActionHandler, SerializerMode

# Local
from ._shared import CreateOrUpdateNetworkRuleSerializer


# --------------------------------------------------------------------------------
# > Handler
# --------------------------------------------------------------------------------
class UpdateNetworkRuleHandler(ModelActionHandler):
    """Updates an existing NetworkRule"""

    serializer_mode = SerializerMode.UNIQUE
    serializer = CreateOrUpdateNetworkRuleSerializer

    def main(self):
        """
        Updates the NetworkRule model with the provided data
        :return: HTTP 200 response with the NetworkRule data
        :rtype: Response
        """
        return self.model_update()
