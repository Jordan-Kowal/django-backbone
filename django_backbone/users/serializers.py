"""Serializers for the 'users' app"""

# Django
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

# Personal
from jklib.django.drf.serializers import (
    ImprovedSerializer,
    NoCreateMixin,
    NoUpdateMixin,
    required,
)

# Application
from security.models import SecurityToken

# Local
from .models import User


# --------------------------------------------------------------------------------
# > Mixins
# --------------------------------------------------------------------------------
class WithPasswordMixin:
    """Provides the 'password' and 'confirm_password' fields with validation"""

    password = serializers.CharField(write_only=True, **required())
    confirm_password = serializers.CharField(write_only=True, **required())

    class Meta:
        fields = ["password", "confirm_password"]

    @staticmethod
    def validate_password(value):
        """
        Checks the password strength
        :return: The raw password
        :rtype: str
        """
        validate_password(value)
        return value

    def validate_confirm_password(self, value):
        """
        Checks it matches the provided password
        :return: The provided value
        :rtype: str
        """
        password = self.initial_data["password"]
        if value != password:
            raise serializers.ValidationError("Passwords do not match")
        return value


# --------------------------------------------------------------------------------
# > User Serializers
# --------------------------------------------------------------------------------
class BaseUserSerializer(NoCreateMixin, serializers.ModelSerializer):
    """Base serializer without the password data. Only for updates."""

    class Meta:
        model = User
        fields = ["id", "email", "first_name", "last_name"]
        read_only_fields = ["id"]


class UserCreateSerializer(NoUpdateMixin, WithPasswordMixin, BaseUserSerializer):
    """Extends BaseUserSerializer to provide the password fields. Only for creations."""

    class Meta(BaseUserSerializer.Meta):
        fields = BaseUserSerializer.Meta.fields + WithPasswordMixin.Meta.fields

    def create(self, validated_data):
        """
        :param dict validated_data:
        :return: The created user instance
        :rtype: User
        """
        validated_data.pop("confirm_password")
        return self.Meta.model.create_user(**validated_data)


class BaseUserAdminSerializer(BaseUserSerializer):
    """Same as BaseUserSerializer with access to more fields (made for admins). Only for updates"""

    class Meta(BaseUserSerializer.Meta):
        fields = BaseUserSerializer.Meta.fields + [
            "is_active",
            "is_staff",
            "is_verified",
        ]


class UserAdminCreateSerializer(UserCreateSerializer):
    """Extends BaseUserAdminSerializer to provide the password fields. Only for creations."""

    class Meta(UserCreateSerializer.Meta):
        fields = UserCreateSerializer.Meta.fields + [
            "is_active",
            "is_staff",
            "is_verified",
        ]

    def create(self, validated_data):
        """
        :param dict validated_data:
        :return: The created user instance
        :rtype: User
        """
        validated_data.pop("confirm_password")
        return self.Meta.model.create_user(**validated_data)


# --------------------------------------------------------------------------------
# > Password serializers
# --------------------------------------------------------------------------------
class OverridePasswordSerializer(WithPasswordMixin, ImprovedSerializer):
    """Simple serializer to update a user's password"""

    def update(self, user, validated_data):
        """
        Updates the user's password and returns the instance
        :param User user:
        :param dict validated_data:
        :return: The updated user
        :rtype: User
        """
        user.set_password(validated_data["password"])
        user.save()
        return user


class UpdatePasswordSerializer(WithPasswordMixin, ImprovedSerializer):
    """Similar to 'OverridePasswordSerializer' but asks for the user's current password"""

    current_password = serializers.CharField(write_only=True, **required())

    class Meta:
        fields = WithPasswordMixin.Meta.fields + ["current_password"]

    def update(self, user, validated_data):
        """
        Updates the user's password and returns the instance
        :param User user:
        :param dict validated_data:
        :return: The updated user
        :rtype: User
        """
        user.set_password(validated_data["password"])
        user.save()
        return user

    def validate_current_password(self, current_password):
        """
        Checks the value matches the user's current password
        :param str current_password:
        :return: The raw password
        :rtype: str
        """
        user = self.instance
        if not user.check_password(current_password):
            raise serializers.ValidationError("Invalid current password")
        return current_password


class PasswordResetSerializer(WithPasswordMixin, ImprovedSerializer):
    """Similar to 'OverridePasswordSerializer' but it uses a token to get the user instance"""

    token = serializers.CharField(write_only=True, **required())

    class Meta:
        fields = WithPasswordMixin.Meta.fields + ["token"]

    def create(self, validated_data):
        """
        Consumes the token, updates the user's password, and returns the updated user
        :param dict validated_data:
        :return: The found and updated user instance
        :rtype: User
        """
        token_instance = validated_data["token"]
        user = token_instance.user
        user.set_password(validated_data["password"])
        user.save()
        token_instance.consume_token()
        return user

    @staticmethod
    def validate_token(value):
        """
        Checks the token value matches an active RESET Token, and returns its instance
        :param str value:
        :return: The fetched token instance
        :rtype: Token
        """
        token_type, _ = User.RESET_TOKEN
        token_instance = SecurityToken.fetch_token_instance(value, token_type)
        if token_instance is None:
            raise serializers.ValidationError("Invalid or expired token")
        return token_instance


class RequestPasswordResetSerializer(ImprovedSerializer):
    """Serializer that asks for an email address"""

    email = serializers.EmailField(**required())

    class Meta:
        fields = ["email"]


# --------------------------------------------------------------------------------
# > Others
# --------------------------------------------------------------------------------
class VerifySerializer(ImprovedSerializer):
    """Serializer that checks for a VERIFY token"""

    token = serializers.CharField(write_only=True, **required())

    class Meta:
        fields = ["token"]

    def create(self, validated_data):
        """
        Consumes to token, flags the corresponding user as verified and returns its instance
        :param dict validated_data:
        :return: The user instance and whether it was updated
        :rtype: User, bool
        """
        token_instance = validated_data["token"]
        user = token_instance.user
        has_changed = False
        if not user.is_verified:
            user.is_verified = True
            user.save()
            has_changed = True
        token_instance.consume_token()
        return user, has_changed

    @staticmethod
    def validate_token(value):
        """
        Checks the token value matches an active VERIFY Token, and returns its instance
        :param str value:
        :return: The fetched token instance
        :rtype: Token
        """
        token_type, _ = User.VERIFY_TOKEN
        token_instance = SecurityToken.fetch_token_instance(value, token_type)
        if token_instance is None:
            raise serializers.ValidationError("Invalid or expired token")
        return token_instance
