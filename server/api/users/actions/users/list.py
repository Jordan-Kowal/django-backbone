"""Handler for the 'list' action"""


# Django
from django.contrib.auth.models import User
from rest_framework.serializers import ModelSerializer

# Personal
from jklib.django.drf.actions import ModelActionHandler, SerializerMode

# Local
from ._shared import user_representation


# --------------------------------------------------------------------------------
# > Serializers
# --------------------------------------------------------------------------------
class ListUserSerializer(ModelSerializer):
    """Model serializer to fetch data from all the existing users"""

    class Meta:
        """Meta class to setup the serializer"""

        model = User

    def to_representation(self, user):
        """
        (For each user) Returns the formatted user data
        :param User user: The targeted user instance
        :return: Dict containing our user data
        :rtype: dict
        """
        return user_representation(user)


# --------------------------------------------------------------------------------
# > Handler
# --------------------------------------------------------------------------------
class ListUserHandler(ModelActionHandler):
    """Fetches the list of existing users"""

    serializer_mode = SerializerMode.UNIQUE
    serializer = ListUserSerializer

    def main(self):
        """
        Fetches all the users from the database
        :return: HTTP 200 response with the data for each user
        :rtype: Response
        """
        return self.model_list()
