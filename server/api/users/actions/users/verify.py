"""Handler for the 'verify' action"""

# Django
from rest_framework.response import Response
from rest_framework.serializers import CharField, ValidationError
from rest_framework.status import HTTP_204_NO_CONTENT

# Personal
from jklib.django.drf.actions import ActionHandler
from jklib.django.drf.serializers import NotEmptySerializer, required

# Local
from ...models import Token
from ._shared import validate_token


# --------------------------------------------------------------------------------
# > Serializers
# --------------------------------------------------------------------------------
class VerifySerializer(NotEmptySerializer):
    """Serializer that checks if a provided security token is valid and returns the Token instance"""

    # ----------------------------------------
    # Fields
    # ----------------------------------------
    token = CharField(**required())

    @staticmethod
    def validate_token(token):
        """
        Checks if the Token matching the provided token value exists and is valid
        Returns the Token instance found
        :param str token: A long string of character that represents a token
        :return: Token instance that matches the provided token value
        :rtype: Token
        """
        return validate_token(token, "verify")


# --------------------------------------------------------------------------------
# > Handler
# --------------------------------------------------------------------------------
class VerifyHandler(ActionHandler):
    """Verifies the user if the provided token is valid"""

    serializer = VerifySerializer

    def main(self):
        """
        Verifies the user and sends him the welcome email
        :return: A 204 OK response with no payload
        :rtype: Response
        """
        serializer = self.get_valid_serializer(data=self.data)
        token_instance = serializer.validated_data["token"]
        self._update_user(token_instance.user)
        token_instance.consume_token()
        return Response(None, HTTP_204_NO_CONTENT)

    @staticmethod
    def _update_user(user):
        """
        Verifies and notifies the user only if he is not already verified
        :param User user:
        """
        profile = user.profile
        if not profile.is_verified:
            profile.is_verified = True
            profile.save()
            profile.send_welcome_email()
