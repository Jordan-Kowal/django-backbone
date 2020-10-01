"""Handler for the 'override_password' action"""

# Django
from rest_framework.response import Response
from rest_framework.serializers import CharField
from rest_framework.status import HTTP_204_NO_CONTENT

# Personal
from jklib.django.drf.actions import ActionHandler
from jklib.django.drf.serializers import NotEmptySerializer, required

# Local
from ._shared import validate_password_confirmation, validate_user_password


# --------------------------------------------------------------------------------
# > Serializer
# --------------------------------------------------------------------------------
class OverridePasswordSerializer(NotEmptySerializer):
    """Serializer to force a new password"""

    # ----------------------------------------
    # Fields
    # ----------------------------------------
    password = CharField(write_only=True, **required())
    confirm_password = CharField(write_only=True, **required())

    # ----------------------------------------
    # Behavior
    # ----------------------------------------
    def update(self, user, validated_data):
        """
        Updates the provided user with a new password hash
        :param User user: The User instance to update
        :param validated_data: Validated data of the serializer
        :return: The updated user instance
        :rtype: User
        """
        hashed_password = validated_data["password"]
        user.password = hashed_password
        user.save()
        return user

    # ----------------------------------------
    # Validation
    # ----------------------------------------
    @staticmethod
    def validate_password(password):
        """
        The new password must pass the security tests before being hashed
        :param str password: The new password
        :return: Hash of the new password
        :rtype: str
        """
        return validate_user_password(password)

    def validate_confirm_password(self, confirm_password):
        """
        Checks that the password has been typed correctly twice
        :param str confirm_password: The password confirmation field
        :return: The unchanged password confirmation
        :rtype: str
        """
        new_password = self.initial_data["password"]
        return validate_password_confirmation(new_password, confirm_password)


# --------------------------------------------------------------------------------
# > Handler
# --------------------------------------------------------------------------------
class OverridePasswordHandler(ActionHandler):
    """
    Overrides the password of the targeted user without sending a notification email
    Only admins should be allowed to perform this action
    """

    serializer_mode = "normal"
    serializer = OverridePasswordSerializer

    def main(self):
        """
        Overrides the user's password without sending a notification email
        :return: HTTP 204 with no payload once the user has been updated
        :rtype: Response
        """
        user = self.viewset.get_object()
        serializer = self.get_valid_serializer(user, data=self.data)
        serializer.save()
        return Response(None, status=HTTP_204_NO_CONTENT)
