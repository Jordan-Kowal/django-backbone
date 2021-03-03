"""Handler for the 'clear' action"""

# Django
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK

# Personal
from jklib.django.drf.actions import ActionHandler, SerializerMode

# Local
from ._shared import network_rule_representation


# --------------------------------------------------------------------------------
# > Handler
# --------------------------------------------------------------------------------
class ClearNetworkRuleHandler(ActionHandler):
    """Clears an existing NetworkRule"""

    serializer_mode = SerializerMode.NONE
    serializer = None

    def main(self):
        """
        Clears an existing NetworkRule (only if eligible)
        :return: HTTP 200 response with the NetworkRule data + whether it actually changed
        :rtype: Response
        """
        instance = self.viewset.get_object()
        changed = False
        # Update only if necessary
        if (
            instance.expires_on is not None
            or instance.active
            or instance.status != instance.Status.NONE
        ):
            instance.clear()
            changed = True
        data = network_rule_representation(instance)
        data["updated"] = changed
        return Response(data, status=HTTP_200_OK)
