"""Handler for the 'update_password' action"""

# Django
from django.contrib.auth.hashers import make_password
from rest_framework.response import Response
from rest_framework.serializers import CharField, ValidationError
from rest_framework.status import HTTP_204_NO_CONTENT

# Personal
from jklib.django.drf.actions import ActionHandler
from jklib.django.drf.serializers import NotEmptySerializer, required

# Local
from ._shared import validate_password_confirmation, validate_user_password


# --------------------------------------------------------------------------------
# > Serializer
# --------------------------------------------------------------------------------
class UpdatePasswordSerializer(NotEmptySerializer):
    """
    Serializer to update a user password while he is authenticated
    Requires the current password for it to work
    """

    # ----------------------------------------
    # Fields
    # ----------------------------------------
    current_password = CharField(write_only=True, **required())
    new_password = CharField(write_only=True, **required())
    confirm_new_password = CharField(write_only=True, **required())

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
        new_hashed_password = validated_data["new_password"]
        user.password = new_hashed_password
        user.save()
        return user

    # ----------------------------------------
    # Validation
    # ----------------------------------------
    def validate_current_password(self, current_password):
        """
        Must provide the right current password for the user, as a security measure
        :param str current_password: Should be the user's current password
        :return: Hash of the current password
        :rtype: str
        """
        user = self.instance
        if not user.check_password(current_password):
            raise ValidationError("Current password is incorrect")
        return make_password(current_password)

    @staticmethod
    def validate_new_password(new_password):
        """
        The new password must pass the security tests before being hashed
        :param str new_password: The new password
        :return: Hash of the new password
        :rtype: str
        """
        return validate_user_password(new_password)

    def validate_confirm_new_password(self, confirm_new_password):
        """
        Checks that the password has been typed correctly twice
        :param str confirm_new_password: The password confirmation field
        :return: The unchanged password confirmation
        :rtype: str
        """
        new_password = self.initial_data["new_password"]
        return validate_password_confirmation(new_password, confirm_new_password)


# --------------------------------------------------------------------------------
# > Handler
# --------------------------------------------------------------------------------
class UpdatePasswordHandler(ActionHandler):
    """Updates the password of the authenticated user"""

    serializer = UpdatePasswordSerializer

    def main(self):
        """
        Updates the user's password and sends him a notification email
        :return: HTTP 204 with no payload once the user has been updated
        :rtype: Response
        """
        serializer = self.get_valid_serializer(self.user, data=self.data, partial=True)
        serializer.save()
        self.user.profile.send_password_update_email()
        return Response(None, status=HTTP_204_NO_CONTENT)
