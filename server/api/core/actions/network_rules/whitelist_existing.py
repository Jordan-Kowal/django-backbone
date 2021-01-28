"""Handler for the 'whitelist_existing' action"""

# Django
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_409_CONFLICT

# Personal
from jklib.django.drf.actions import ModelActionHandler, SerializerMode

# Local
from ._shared import ActivateNetworkRuleSerializer, network_rule_representation


# --------------------------------------------------------------------------------
# > Handler
# --------------------------------------------------------------------------------
class WhitelistNetworkRuleHandler(ModelActionHandler):
    """
    Updates a NetworkRule to whitelist its IP
    Missing fields will be defaulted and will override the instance current value
    """

    serializer_mode = SerializerMode.UNIQUE
    serializer = ActivateNetworkRuleSerializer

    def main(self):
        """
        Whitelists an existing NetworkRule instance
        :return: HTTP 200 response with the NetworkRule data
        :rtype: Response
        """
        instance = self.viewset.get_object()
        serializer = self.get_valid_serializer(instance, data=self.data)
        payload = {
            "end_date": serializer.validated_data.get("expires_on", None),
            "comment": serializer.validated_data.get("comment", None),
            "override": serializer.validated_data.get("override", False),
        }
        # Override condition
        if instance.is_blacklisted and not payload["override"]:
            return Response(None, status=HTTP_409_CONFLICT)
        # Blacklists the IP
        instance.whitelist(**payload)
        data = network_rule_representation(instance)
        return Response(data, status=HTTP_200_OK)
