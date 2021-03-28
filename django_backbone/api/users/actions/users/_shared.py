"""Reusable classes, functions and variables available for all our user services"""

# Django
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework.serializers import ModelSerializer, ValidationError

# Local
from ...models import Token


# --------------------------------------------------------------------------------
# > Serializers
# --------------------------------------------------------------------------------
class RetrieveUserSerializer(ModelSerializer):
    """Model serializer to fetch data from the User instance"""

    class Meta:
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
        "is_staff": user.is_staff,
        "last_login": user.last_login,
        "profile": {"is_verified": profile.is_verified,},
    }


def validate_email_is_still_unique(current_email, new_email):
    """
    If the email changes, checks that it is still unique
    :param str current_email: The current email of our user
    :param str new_email: The new email provided
    :raises ValidationError: If another user already uses this email address
    :return: The email initial data
    :rtype: str
    """
    if new_email != current_email:
        users = User.objects.filter(email=new_email)
        if len(users) > 0:
            raise ValidationError("This email is already taken")
    return new_email


def validate_password_confirmation(password, password_confirmation):
    """
    Checks that the password has been typed correctly twice
    :param str password: The password field
    :param str password_confirmation: The password confirmation field
    :raises ValidationError: When the password does not match the confirmation
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
    :raises ValidationError: If the token is expired or invalid
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
