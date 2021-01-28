"""Handler for the 'list' action"""

# Personal
from jklib.django.drf.actions import ModelActionHandler, SerializerMode

# Local
from ._shared import RetrieveNetworkRuleSerializer


# --------------------------------------------------------------------------------
# > Handler
# --------------------------------------------------------------------------------
class ListNetworkRulesHandler(ModelActionHandler):
    """Fetches the info of all existing NetworkRules"""

    serializer_mode = SerializerMode.UNIQUE
    serializer = RetrieveNetworkRuleSerializer

    def main(self):
        """
        Fetches all existing NetworkRule instances data
        :return: HTTP 200 response with the instance data
        :rtype: Response
        """
        return self.model_list()
