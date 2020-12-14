"""Handler for the 'list' action"""

# Django
from rest_framework.response import Response

# Personal
from jklib.django.drf.actions import ModelActionHandler, SerializerMode

# Local
from ._shared import RetrieveContactSerializer


# --------------------------------------------------------------------------------
# > Handler
# --------------------------------------------------------------------------------
class ListContactHandler(ModelActionHandler):
    """Fetches all Contact instances in the database"""

    serializer_mode = SerializerMode.UNIQUE
    serializer = RetrieveContactSerializer

    def main(self):
        """
        Fetches and returns all the Contact instances in the right format
        :return: HTTP 200 with all of our instances data
        :rtype: Response
        """
        return self.model_list()
