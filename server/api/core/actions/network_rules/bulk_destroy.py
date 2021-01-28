"""Handler for the 'bulk_destroy' action"""

# Django
from rest_framework.response import Response

# Personal
from jklib.django.drf.actions import ModelActionHandler, SerializerMode
from jklib.django.drf.serializers import IdListSerializer


# --------------------------------------------------------------------------------
# > Handler
# --------------------------------------------------------------------------------
class BulkDestroyNetworkRulesHandler(ModelActionHandler):
    """Deletes the NetworkRule instances matching the given IDs"""

    serializer_mode = SerializerMode.UNIQUE
    serializer = IdListSerializer

    def main(self):
        """
        Filters the instances with the provided IDs and removes them
        :return: HTTP 204 response without data
        :rtype: Response
        """
        return self.model_bulk_destroy()
