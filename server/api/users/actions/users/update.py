"""Handler for the 'update' action"""


# Personal
from jklib.django.drf.actions import ModelActionHandler

# Local
from ._shared import UpdateAdminSerializer, UpdateUserSerializer


# --------------------------------------------------------------------------------
# > Handler
# --------------------------------------------------------------------------------
class UpdateUserHandler(ModelActionHandler):
    """Updates a user data"""

    serializer_mode = "user"
    serializer = {"user": UpdateUserSerializer, "admin": UpdateAdminSerializer}

    def main(self):
        """
        Updates the user based on the data from the serializer
        :return: HTTP 200 response with the updated user data
        :rtype: Response
        """
        return self.model_update()
