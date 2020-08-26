"""Handler for the 'perform_password_reset' action"""

# Django
from rest_framework.response import Response
from rest_framework.serializers import CharField
from rest_framework.status import HTTP_204_NO_CONTENT

# Personal
from jklib.django.drf.actions import ActionHandler
from jklib.django.drf.serializers import NotEmptySerializer, required

# Local
from ...models import Token
from ._shared import (
    validate_password_confirmation,
    validate_token,
    validate_user_password,
)


# --------------------------------------------------------------------------------
# > Serializers
# --------------------------------------------------------------------------------
class PerformPasswordResetSerializer(NotEmptySerializer):
    """
    Serializer that uses a Token to find a user and checks if his password can be updated
    Does not perform the actual model update, but stores the valid Token instance in its validated_data
    This allows us to perform the update in the ActionHandler
    """

    # ----------------------------------------
    # Fields
    # ----------------------------------------
    new_password = CharField(**required())
    confirm_new_password = CharField(**required())
    token = CharField(**required())

    # ----------------------------------------
    # Validation
    # ----------------------------------------
    def validate_confirm_new_password(self, confirm_new_password):
        """
        Checks that the password has been typed correctly twice
        :param str confirm_new_password: The password confirmation field
        :return: The unchanged password confirmation
        :rtype: str
        """
        new_password = self.initial_data["new_password"]
        return validate_password_confirmation(new_password, confirm_new_password)

    @staticmethod
    def validate_new_password(new_password):
        """
        The new password must pass the security tests before being hashed
        :param str new_password: The new password
        :return: Hash of the new password
        :rtype: str
        """
        return validate_user_password(new_password)

    @staticmethod
    def validate_token(token):
        """
        Checks if the Token matching the provided token value exists and is valid
        Returns the Token instance found
        :param str token: A long string of character that represents a token
        :return: Token instance that matches the provided token value
        :rtype: Token
        """
        return validate_token(token, "reset")


# --------------------------------------------------------------------------------
# > Handler
# --------------------------------------------------------------------------------
class PerformPasswordResetHandler(ActionHandler):
    """
    Using a one-time security token, finds the matching user and updates his password
    This service is part of the 'reset' process and is available to unauthenticated users
    The user will receive an email if his password was updated
    """

    serializer = PerformPasswordResetSerializer

    def main(self):
        """
        Updates the user's password if the token is valid
        :return: A 204 OK response with no payload
        :rtype: Response
        """
        user, password_hash, token_instance = self._validate_serializer()
        self._update_user(user, password_hash)
        token_instance.consume_token()
        return Response(None, status=HTTP_204_NO_CONTENT)

    @staticmethod
    def _update_user(user, password_hash):
        """
        Updates the user's password in the database and sends him a notification email
        :param User user: The targeted User instance
        :param str password_hash: The new password hash
        """
        user.password = password_hash
        user.save()
        user.profile.send_password_update_email()

    def _validate_serializer(self):
        """
        Validates the serializers and returns useful information
        :return: The User instance attached to the token, the password hash, and the Toek instance
        :rtype: (User, str, Token)
        """
        serializer = self.get_valid_serializer(data=self.data)
        validated_data = serializer.validated_data
        token_instance = validated_data["token"]
        password_hash = validated_data["new_password"]
        user = token_instance.user
        return user, password_hash, token_instance
