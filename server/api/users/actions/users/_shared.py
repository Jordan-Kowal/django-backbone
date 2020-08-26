"""Reusable classes, functions and variables available for all our user services"""

# Django
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework.serializers import BooleanField, ModelSerializer, ValidationError

# Personal
from jklib.django.drf.serializers import NotEmptyModelSerializer, required

# Local
from ...models import Token


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
        Will update both the User and its Profile instance
        :param User user: The User instance to update
        :param dict validated_data: Validated data of the serializer
        :return: The updated user instance
        :rtype: User
        """
        user.email = validated_data.get("email", user.email)
        user.first_name = validated_data.get("first_name", user.first_name)
        user.last_name = validated_data.get("last_name", user.last_name)
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
        If the email changes, checks that it is still unique
        :param str email: The provided email
        :return: The email initial data
        :rtype: str
        """
        if email != self.instance.email:
            users = User.objects.filter(email=email)
            if len(users) > 0:
                raise ValidationError("This email is already taken")
        return email


# --------------------------------------------------------------------------------
# > Functions
# --------------------------------------------------------------------------------
def user_representation(user):
    """
    Returns a dict with our user data, to be used in serializer output
    :param User user: The user instance we want to format
    :return: Dict with our user data, including its profile
    :rtype: dict
    """
    profile = user.profile
    return {
        "id": user.id,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email,
        "is_active": user.is_active,
        "last_login": user.last_login,
        "profile": {"is_verified": profile.is_verified,},
    }


def validate_password_confirmation(password, password_confirmation):
    """
    Checks that the password has been typed correctly twice
    :param str password: The password field
    :param str password_confirmation: The password confirmation field
    :return: The unchanged password confirmation
    :rtype: str
    """
    if password_confirmation != password:
        raise ValidationError("Passwords do not match")
    return password_confirmation


def validate_token(token_value, token_type):
    """
    Checks if the Token matching the provided token value exists and is valid
    Returns the Token instance found
    :param str token_value: A long string of character that represents a token
    :param str token_type: Type of our token
    :return: Token instance that matches the provided token value
    :rtype: Token
    """
    token_instance = Token.fetch_token_instance(token_value, token_type)
    if token_instance is None:
        raise ValidationError("Invalid or expired token")
    return token_instance


def validate_user_password(password):
    """
    The new password must pass the security tests before being hashed
    :param str password: The new password
    :return: Hash of the new password
    :rtype: str
    """
    validate_password(password)
    return make_password(password)
