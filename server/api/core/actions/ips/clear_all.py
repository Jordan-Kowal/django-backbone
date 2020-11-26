"""Handler for the 'clear_all' action"""

# Django
from django.db.models import Q
from rest_framework.response import Response
from rest_framework.serializers import ChoiceField
from rest_framework.status import HTTP_204_NO_CONTENT

# Personal
from jklib.django.drf.actions import ActionHandler, SerializerMode
from jklib.django.drf.serializers import ImprovedSerializer

# Local
from ...models import IpAddress
from ._shared import STATUS_CHOICES, validate_status


# --------------------------------------------------------------------------------
# > Serializer
# --------------------------------------------------------------------------------
class ClearAllIpsSerializer(ImprovedSerializer):
    """Simple INPUT serializer with a status field"""

    status = ChoiceField(choices=STATUS_CHOICES, allow_null=True, allow_blank=True)

    @staticmethod
    def validate_status(status):
        """
        Converts the status to enum and checks if it is a valid option
        :param status: The provided status for the IpAddress
        :type status: str or int
        :return: The status converted to its enum integer value
        :rtype: int
        """
        if status is None or status == "":
            return None
        return validate_status(status)


# --------------------------------------------------------------------------------
# > Handler
# --------------------------------------------------------------------------------
class ClearAllIpsHandler(ActionHandler):
    """Clears all clearable existing ips"""

    serializer_mode = SerializerMode.UNIQUE
    serializer = ClearAllIpsSerializer

    def main(self):
        """
        Clears all eligible IPs (can be restricted to a specific ip status)
        :return: HTTP 204 response with no data
        :rtype: Response
        """
        serializer = self.get_valid_serializer(data=self.data)
        ip_status = serializer.validated_data.get("status", None)
        query = self._build_query(ip_status)
        eligible_ips = IpAddress.objects.filter(query)
        for ip in eligible_ips:
            ip.clear()
        return Response(None, status=HTTP_204_NO_CONTENT)

    @staticmethod
    def _build_query(status=None):
        """
        Builds the query to fetch the requested IPs
        If a status is not provided, we fetch all IPs that could benefit from clearing
        :param IpStatus status: The status used to fetch IPs
        :return: Query to be used to fetch our eligible IPs
        :rtype: Q
        """
        # If not status is provided, we fetch IPs based on the field that will/should be reset
        if status is None:
            query = (
                Q(active=True)
                | ~Q(expires_on=None)
                | ~Q(status=IpAddress.IpStatus.NONE)
            )
        # Else we simply fetch those of said status (NONE, WHITELISTED, OR BLACKLISTED
        else:
            query = Q(status=status)
        return query
