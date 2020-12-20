"""Handler for the 'login' action"""

# Django
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework.serializers import ValidationError
from rest_framework.status import HTTP_200_OK

# Personal
from jklib.django.drf.actions import ActionHandler
from jklib.django.drf.serializers import NotEmptyModelSerializer, required


# --------------------------------------------------------------------------------
# > Serializers
# --------------------------------------------------------------------------------
class LoginSerializer(NotEmptyModelSerializer):
    """Checks the user credentials (email/password) but does not actually login the user"""

    # ----------------------------------------
    # Behavior
    # ----------------------------------------
    class Meta:
        """Meta class to setup the serializer"""

        model = User
        fields = [
            "email",
            "password",
        ]
        extra_kwargs = {
            "email": {"write_only": True, **required()},
            "password": {"write_only": True, **required()},
        }

    # ----------------------------------------
    # Validation
    # ----------------------------------------
    def validate(self, validated_data):
        """
        Checks the user's credentials without login him
        :param dict validated_data: The data after the individual validations
        :raises ValidationError: If the user's credentials are invalid
        :return: The validated data using the parent method
        :rtype: dict
        """
        email = validated_data["email"]
        password = validated_data["password"]
        user = authenticate(username=email, password=password)
        if user is None:
            raise ValidationError("Invalid credentials")
        return super().validate(validated_data)

    @staticmethod
    def validate_email(email):
        """
        Makes the 'email' field required
        :param str email: The provided email address
        :raises ValidationError: If the email is missing or empty
        :return: The trimmed email address
        :rtype: str
        """
        email = email.strip()
        if email == "":
            raise ValidationError("Email is required")
        return email

    @staticmethod
    def validate_password(password):
        """
        Makes the 'password' field required
        :param str password: The user's password
        :raises ValidationError: If the password is empty or missing
        :return: The trimmed password
        :rtype: str
        """
        password = password.strip()
        if password == "":
            raise ValidationError("Password is required")
        return password


# --------------------------------------------------------------------------------
# > Handler
# --------------------------------------------------------------------------------
class LoginHandler(ActionHandler):
    """Action to login a user when valid credentials are provided"""

    serializer = LoginSerializer

    def main(self):
        """Logins the user if his credentials are correct"""
        serializer = self.viewset.get_valid_serializer(data=self.data)
        email = serializer.validated_data["email"]
        password = serializer.validated_data["password"]
        user = authenticate(username=email, password=password)
        login(self.request, user)
        return Response(None, HTTP_200_OK)
