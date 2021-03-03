"""Handler for the 'update' action"""


# Django
from django.contrib.auth.models import User
from rest_framework.serializers import BooleanField

# Personal
from jklib.django.drf.actions import ModelActionHandler, SerializerMode
from jklib.django.drf.serializers import NotEmptyModelSerializer, required

# Local
from ._shared import user_representation, validate_email_is_still_unique


# --------------------------------------------------------------------------------
# > Serializers
# --------------------------------------------------------------------------------
class UpdateAdminSerializer(NotEmptyModelSerializer):
    """
    Model serializer to update a user's data, destined to ADMIN users
    Can update more fields than the basic UpdateUserSerializer
    Because the email is also the username, it is required and must be unique
    """

    is_verified = BooleanField(required=False)

    # ----------------------------------------
    # Behavior
    # ----------------------------------------
    class Meta:
        """Meta class to setup the serializer"""

        model = User
        fields = [
            "first_name",
            "last_name",
            "email",
            "is_active",
            "is_staff",
            "is_verified",
        ]
        extra_kwargs = {
            "email": {**required()},
        }

    def update(self, user, validated_data):
        """
        Behavior when saving the serializer associated to an existing user
        Will update both the User and its Profile instance
        :param User user: The User instance to update
        :param dict validated_data: Validated data of the serializer
        :return: The updated user instance
        :rtype: User
        """
        # Updating the models
        user.email = validated_data.get("email", user.email)
        user.first_name = validated_data.get("first_name", user.first_name)
        user.last_name = validated_data.get("last_name", user.last_name)
        user.is_active = validated_data.get("is_active", user.is_active)
        user.is_staff = validated_data.get("is_staff", user.is_staff)
        profile = user.profile
        profile.is_verified = validated_data.get("is_verified", profile.is_verified)
        # Saving the models (starting with deepest)
        profile.save()
        user.save()
        return user

    def to_representation(self, user):
        """
        Returns the formatted user data
        :param User user: The targeted user instance
        :return: Dict containing our user data
        :rtype: dict
        """
        return user_representation(user)

    # ----------------------------------------
    # Validation
    # ----------------------------------------
    def validate_email(self, email):
        """
        Checks that the new email is still unique
        :param str email: The provided email
        :return: The email initial data
        :rtype: str
        """
        return validate_email_is_still_unique(self.instance.email, email)


class UpdateUserSerializer(NotEmptyModelSerializer):
    """
    Model serializer to update a user data
    Only 3 fields are editable: email, first_name, last_name
    Because the email is also the username, it is required and must be unique
    """

    # ----------------------------------------
    # Behavior
    # ----------------------------------------
    class Meta:
        """Meta class to setup the serializer"""

        model = User
        fields = [
            "email",
            "first_name",
            "last_name",
        ]
        extra_kwargs = {
            "email": {**required()},
        }

    def update(self, user, validated_data):
        """
        Behavior when saving the serializer associated to an existing user
        :param User user: The User instance to update
        :param dict validated_data: Validated data of the serializer
        :return: The updated user instance
        :rtype: User
        """
        # Trimming the name
        first_name = validated_data.get("first_name", user.first_name).strip()
        last_name = validated_data.get("last_name", user.last_name).strip()
        # Updating
        user.email = validated_data.get("email", user.email)
        user.first_name = first_name
        user.last_name = last_name
        user.save()
        return user

    def to_representation(self, user):
        """
        Returns the formatted user data
        :param User user: The targeted user instance
        :return: Dict containing our user data
        :rtype: dict
        """
        return user_representation(user)

    # ----------------------------------------
    # Validation
    # ----------------------------------------
    def validate_email(self, email):
        """
        Checks that the new email is still unique
        :param str email: The provided email
        :return: The email initial data
        :rtype: str
        """
        return validate_email_is_still_unique(self.instance.email, email)


# --------------------------------------------------------------------------------
# > Handler
# --------------------------------------------------------------------------------
class UpdateUserHandler(ModelActionHandler):
    """Updates a user data"""

    serializer_mode = SerializerMode.ROLE_BASED
    serializer = {"user": UpdateUserSerializer, "admin": UpdateAdminSerializer}

    def main(self):
        """
        Updates the user based on the data from the serializer
        :return: HTTP 200 response with the updated user data
        :rtype: Response
        """
        return self.model_update()
