"""Handler for the 'retrieve' action"""


# Personal
from jklib.django.drf.actions import ModelActionHandler, SerializerMode

# Local
from ._shared import RetrieveUserSerializer


# --------------------------------------------------------------------------------
# > Handler
# --------------------------------------------------------------------------------
class RetrieveUserHandler(ModelActionHandler):
    """Fetches a user's data"""

    serializer_mode = SerializerMode.UNIQUE
    serializer = RetrieveUserSerializer

    def main(self):
        """
        Fetches the User instance data
        :return: HTTP 200 response with the user data
        :rtype: Response
        """
        return self.model_retrieve()
