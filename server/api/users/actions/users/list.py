"""Handler for the 'list' action"""


# Personal
from jklib.django.drf.actions import ModelActionHandler, SerializerMode

# Local
from ._shared import RetrieveUserSerializer


# --------------------------------------------------------------------------------
# > Handler
# --------------------------------------------------------------------------------
class ListUserHandler(ModelActionHandler):
    """Fetches the list of existing users"""

    serializer_mode = SerializerMode.UNIQUE
    serializer = RetrieveUserSerializer

    def main(self):
        """
        Fetches all the users from the database
        :return: HTTP 200 response with the data for each user
        :rtype: Response
        """
        return self.model_list()
