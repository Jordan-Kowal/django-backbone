"""Shared utilities for the contact API test"""

# Local
from ....models import Contact

# --------------------------------------------------------------------------------
# > Constants
# --------------------------------------------------------------------------------
BASE_URL = "/api/contact"
DEFAULT_VALUES = {
    "ip": "1.1.1.1",
    "name": "Default name",
    "email": "fake.default.email@fake.domain",
    "subject": "Default subject for the contact",
    "body": "Default content for the body of the contact request",
    "user": None,
}


# --------------------------------------------------------------------------------
# > Assert
# --------------------------------------------------------------------------------
def assert_response_matches_instance(response_data, instance):
    """
    Compares the response data to the Contact instance
    :param dict response_data: Contact data from the service response
    :param Contact instance: Contact instance from the database
    """
    assert response_data["id"] == instance.id
    assert response_data["ip"] == instance.ip
    assert response_data["name"] == instance.name
    assert response_data["email"] == instance.email
    assert response_data["subject"] == instance.subject
    assert response_data["body"] == instance.body
    assert_response_user_matches_instance_user(response_data, instance)


def assert_response_user_matches_instance_user(response_data, instance):
    """
    Compares the user data from the response and the Contact instance
    :param dict response_data: Contact data from the service response
    :param Contact instance: Contact instance from the database
    """
    if instance.user is None:
        assert response_data["user"] is None
    else:
        user_data = response_data["user"]
        assert user_data["id"] == instance.user.id
        assert user_data["first_name"] == instance.user.first_name
        assert user_data["last_name"] == instance.user.last_name
        assert user_data["email"] == instance.user.email
        assert user_data["is_active"] == instance.user.is_active
        assert user_data["is_verified"] == instance.user.profile.is_verified


# --------------------------------------------------------------------------------
# > Helpers
# --------------------------------------------------------------------------------
def create_contact(**values):
    """
    Creates an Contact instance using default parameters and the one provided
    :param values: Parameters to override the default values
    :return: The created Contact instance
    :rtype: Contact
    """
    data = {**DEFAULT_VALUES, **values}
    return Contact.objects.create(**data)
