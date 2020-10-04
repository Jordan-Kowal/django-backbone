"""Handler for the 'create' action"""

# Django
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework.serializers import CharField, ValidationError
from rest_framework.status import HTTP_201_CREATED

# Personal
from jklib.django.drf.actions import ActionHandler, SerializerMode
from jklib.django.drf.serializers import NotEmptyModelSerializer, required

# Local
from ._shared import (
    user_representation,
    validate_password_confirmation,
    validate_user_password,
)


# --------------------------------------------------------------------------------
# > Serializers
# --------------------------------------------------------------------------------
class CreateUserSerializer(NotEmptyModelSerializer):
    """
    Serializer to create a user with some customization:
        Added custom field "confirm_password" to avoid typos
        Password must be secure and will be automatically hashed
        Email will be used as auth, so it becomes required and unique
    """

    # ----------------------------------------
    # Custom Fields
    # ----------------------------------------
    confirm_password = CharField(write_only=True, **required())

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
            "password",
            "confirm_password",
        ]
        extra_kwargs = {
            "password": {"write_only": True, **required()},
            "email": {**required()},
        }

    def create(self, validated_data):
        """
        Overridden to remove the custom field 'confirm_password' from the data
        :param dict validated_data: Validated data of the serializer
        :return: The created user model
        :rtype: User
        """
        validated_data.pop("confirm_password", None)
        return super().create(validated_data)

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
    def validate_confirm_password(self, confirm_password):
        """
        Both password fields must match field
        :param str confirm_password: The password confirmation
        :return: The confirm_password initial data
        :rtype: str
        """
        password = self.initial_data.get("password", None)
        return validate_password_confirmation(password, confirm_password)

    @staticmethod
    def validate_email(email):
        """
        Email must be unique
        :param str email: The provided email
        :return: The email initial data
        :rtype: str
        """
        users = User.objects.filter(email=email)
        if len(users) > 0:
            raise ValidationError("This email is already taken")
        return email

    @staticmethod
    def validate_password(password):
        """
        Checks the password strength and hashes it
        :param str password: The provided password
        :return: The hashed password
        :rtype: str
        """
        return validate_user_password(password)


# --------------------------------------------------------------------------------
# > Handler
# --------------------------------------------------------------------------------
class CreateUserHandler(ActionHandler):
    """Creates a new user and sends him the verification email"""

    serializer_mode = SerializerMode.UNIQUE
    serializer = CreateUserSerializer

    def main(self):
        """
        Creates the user and sends him either the verification or welcome email
        :return: HTTP 201 response with the user data
        :rtype: Response
        """
        serializer = self.get_valid_serializer(data=self.data)
        user = serializer.save()
        if user.profile.is_verified:
            user.profile.send_welcome_email()
        else:
            user.profile.send_verification_email()
        return Response(serializer.data, status=HTTP_201_CREATED)
