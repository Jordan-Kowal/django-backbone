"""Handler for the 'retrieve' action"""

# Django
from rest_framework.response import Response

# Personal
from jklib.django.drf.actions import ModelActionHandler, SerializerMode

# Local
from ._shared import RetrieveContactSerializer


# --------------------------------------------------------------------------------
# > Handler
# --------------------------------------------------------------------------------
class RetrieveContactHandler(ModelActionHandler):
    """Retrieves one Contact instance"""

    serializer_mode = SerializerMode.UNIQUE
    serializer = RetrieveContactSerializer

    def main(self):
        """
        Fetches and returns the Contact data
        :return: HTTP 200 with our Contact data
        :rtype: Response
        """
        return self.model_retrieve()
