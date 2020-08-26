"""Handler for the 'self' action"""

# Django
from rest_framework.response import Response

# Personal
from jklib.django.drf.actions import ModelActionHandler

# Local
from ._shared import RetrieveUserSerializer, UpdateUserSerializer


# --------------------------------------------------------------------------------
# > Handler
# --------------------------------------------------------------------------------
class SelfUserHandler(ModelActionHandler):
    """Allows GET/PUT/PATCH/DELETE request on the currently authenticated user"""

    serializer = {
        "get": RetrieveUserSerializer,
        "patch": UpdateUserSerializer,
        "put": UpdateUserSerializer,
        "delete": None,
    }

    def get(self):
        """
        Fetches the current user data
        :return: HTTP 200 response with the user data
        :rtype: Response
        """
        return self.model_retrieve()

    def put(self):
        """
        Updates the current user based on the data from the serializer
        :return: HTTP 200 response with the updated user data
        :rtype: Response
        """
        return self.model_update()

    def delete(self):
        """
        Deletes the currently authenticated user
        :return: HTTP 204 response with no data
        :rtype: Response
        """
        return self.model_destroy()

    # ----------------------------------------
    # Utility
    # ----------------------------------------
    def get_object(self):
        """
        Overrides the existing function so that the object is the current User
        :return: The currently authenticated user instance
        :rtype: User
        """
        return self.user
