"""Handler for the 'retrieve' action"""

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
class RetrieveUserSerializer(ModelSerializer):
    """Model serializer to fetch data from the User instance"""

    class Meta:
        """Meta class to setup the serializer"""

        model = User

    def to_representation(self, user):
        """
        Returns the formatted user data
        :param User user: The targeted user instance
        :return: Dict containing our user data
        :rtype: dict
        """
        return user_representation(user)


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
