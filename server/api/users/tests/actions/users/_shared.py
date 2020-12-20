"""Shared constants, functions, and classes for ou users API"""


# Django
from django.contrib.auth.models import User

# --------------------------------------------------------------------------------
# > Constants
# --------------------------------------------------------------------------------
USER_SERVICE_URL = "/api/users"


# --------------------------------------------------------------------------------
# > Assertions
# --------------------------------------------------------------------------------
def assert_user_representation_matches_instance(user_response, user_instance):
    """
    Compares a user instance to a user representation
    The representations is expected to come from the "users.actions._shared.user_representation()" function
    :param dict user_response: Output of a "user_representation()"
    :param User user_instance: User instance from the database
    """
    assert user_instance.id == user_response["id"]
    assert user_instance.first_name == user_response["first_name"]
    assert user_instance.last_name == user_response["last_name"]
    assert user_instance.email == user_instance.username == user_response["email"]
    assert user_instance.last_login == user_response["last_login"]
    assert user_instance.profile.is_verified == user_response["profile"]["is_verified"]
