"""Serializers for the 'users' app"""

# Django
from django.contrib.auth.models import User
from rest_framework.serializers import ModelSerializer

# Application
from api.users.models import Profile


# --------------------------------------------------------------------------------
# > Serializers
# --------------------------------------------------------------------------------
class ProfileSerializer(ModelSerializer):
    """Base serializer for the Profile model"""

    class Meta:
        model = Profile
        fields = ["is_verified"]
        read_only_fields = ["is_verified"]


class UserSerializer(ModelSerializer):
    """Base serializer for the User model"""

    profile = ProfileSerializer()

    class Meta:
        model = User
        fields = [
            "id",
            "first_name",
            "last_name",
            "email",
            "is_active",
            "profile",
        ]
        read_only_fields = ["id"]
