"""Serializers for the 'contact' app"""

# Django
from rest_framework.serializers import BooleanField, ModelSerializer

# Application
from api.users.serializers import UserSerializer

# Local
from .models import Contact


# --------------------------------------------------------------------------------
# > Serializers
# --------------------------------------------------------------------------------
class ContactSerializer(ModelSerializer):
    """Basic serializer for Contacts"""

    user = UserSerializer(read_only=True)

    class Meta:
        model = Contact
        fields = [
            "id",
            "ip",
            "user",
            "name",
            "email",
            "subject",
            "body",
        ]
        read_only_fields = ["id", "ip"]  # 'user' as well


class ApiCreateContactSerializer(ContactSerializer):
    """Serializer specifically for the create API"""

    notify_user = BooleanField(default=False, write_only=True)

    class Meta(ContactSerializer.Meta):
        fields = ContactSerializer.Meta.fields + ["notify_user"]

    def create(self, validated_data):
        """Removes the `notify_user` field before creating the instance"""
        validated_data.pop("notify_user", None)
        return self.Meta.model.objects.create(**validated_data)
