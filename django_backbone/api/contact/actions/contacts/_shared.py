"""
Utilities for all our core contact services, such as:
    Serializers
    Representation functions
"""

# Django
from rest_framework.serializers import ModelSerializer

# Local
from ...models import Contact


# --------------------------------------------------------------------------------
# > Serializers
# --------------------------------------------------------------------------------
class RetrieveContactSerializer(ModelSerializer):
    """Model serializer to fetch our Contact data"""

    class Meta:
        """Meta class to setup the serializer"""

        model = Contact

    def to_representation(self, instance):
        """
        (Override) Returns a dict representation of our Contact instance and its User
        :param Contact instance: The Contact instance to represent
        :return: The Contact instance in dict format
        :rtype: dict
        """
        return contact_representation(instance)


# --------------------------------------------------------------------------------
# > Representations
# --------------------------------------------------------------------------------
def contact_representation(contact):
    """
    Returns a dict of our contact data, including its user data
    :param Contact contact: The Contact instance to represent
    :return: The Contact instance in dict format
    :rtype: dict
    """
    return {
        "id": contact.id,
        "ip": contact.ip,
        "name": contact.name,
        "email": contact.email,
        "subject": contact.subject,
        "body": contact.body,
        "user": user_representation(contact.user),
    }


def user_representation(user):
    """
    Representation of a User instance in relation to a Contact instance
    :param user: The user instance related to our contact instance
    :type user: User or None
    :return: The user data in dict format or nothing
    :rtype: dict or None
    """
    if user is None:
        return None
    return {
        "id": user.id,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email,
        "is_active": user.is_active,
        "is_verified": user.profile.is_verified,
    }
