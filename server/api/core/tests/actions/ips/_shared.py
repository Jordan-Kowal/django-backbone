"""Shared constants, functions, and classes for our IP service tests"""

# Built-in
from datetime import date, timedelta

# Personal
from jklib.django.drf.tests import ActionTestCase

# Application
from api.core.models import IpAddress

# --------------------------------------------------------------------------------
# > Constants
# --------------------------------------------------------------------------------
SERVICE_URL = "/api/ips"
DEFAULT_VALUES = {
    "ip": "127.0.0.10",
    "status": IpAddress.IpStatus.NONE,
    "expires_on": date.today() + timedelta(days=60),
    "active": False,
    "comment": "Test",
}


# --------------------------------------------------------------------------------
# > Utilities
# --------------------------------------------------------------------------------
def create_ip_address(**kwargs):
    """
    Creates an IpAddress instance using default parameters and the one provided
    :param kwargs: Parameters to override the default values
    :return: The created IpAddress instance
    :rtype: IpAddress
    """
    data = {**DEFAULT_VALUES, **kwargs}
    return IpAddress.objects.create(**data)


# --------------------------------------------------------------------------------
# > Assertions
# --------------------------------------------------------------------------------
def assert_admin_permissions(
    client, protocol, url, payload, valid_status_code, admin, user
):
    """
    Tests that the service is only available to admin users
    :param APIClient client: The current APIClient used
    :param func protocol: The client method to use (get, post, etc)
    :param str url: The target url
    :param payload: The data payload to send
    :type payload: dict or None
    :param int valid_status_code: The expected status code when the query is successful
    :param User admin: Any admin user
    :param User user: Any non-admin user
    """
    # 401 Not authenticated
    client.logout()
    response = protocol(url, data=payload)
    assert response.status_code == 401
    # 403 Not admin
    client.force_authenticate(user)
    response = protocol(url, data=payload)
    assert response.status_code == 403
    # 201 Admin
    client.logout()
    client.force_authenticate(admin)
    response = protocol(url, data=payload)
    assert response.status_code == valid_status_code


def assert_comment_length(protocol, url, payload, valid_status_code):
    """
    Tests the comment max length
    :param func protocol: The client method to use (get, post, etc)
    :param str url: The target url
    :param payload: The data payload to send
    :type payload: dict or None
    :param int valid_status_code: The expected status code when the query is successful
    """
    # Too long
    payload["comment"] = "a" * (IpAddress.COMMENT_MAX_LENGTH + 1)
    response = protocol(url, data=payload)
    ActionTestCase().assert_field_has_error(response, "comment")
    # Short enough
    payload["comment"] = "a" * IpAddress.COMMENT_MAX_LENGTH
    response = protocol(url, data=payload)
    assert response.status_code == valid_status_code


def assert_expires_on_is_optional(
    protocol, url, payload, valid_status_code, id_, creation=False
):
    """
    Tests that the 'expires_on' gets defaulted if not provided
    :param func protocol: The client method to use (get, post, etc)
    :param str url: The target url
    :param payload: The data payload to send
    :type payload: dict or None
    :param int valid_status_code: The expected status code when the query is successful
    :param int id_: The IpAddress id to fetch and check the instance
    :param bool creation: In creation mode, IP will be removed and the ID incremented
    :return:
    """
    # With date
    expiration_date = (date.today() + timedelta(days=100)).strftime("%Y-%m-%d")
    payload["expires_on"] = expiration_date
    response = protocol(url, data=payload)
    assert response.status_code == valid_status_code
    instance = IpAddress.objects.get(pk=id_)
    assert instance.expires_on.strftime("%Y-%m-%d") == expiration_date
    if creation:
        IpAddress.objects.get(pk=id_).delete()
        id_ += 1
    # Without date
    payload["expires_on"] = None
    response = protocol(url, data=payload)
    assert response.status_code == valid_status_code
    instance = IpAddress.objects.get(pk=id_)
    expected_date = date.today() + timedelta(days=instance.get_default_duration())
    assert instance.expires_on == expected_date
    if creation:
        IpAddress.objects.get(pk=id_).delete()


def assert_override_condition(
    protocol, url, payload, valid_status_code, id_, ip_status
):
    """
    Tests that a blacklisted/whitelisted IP can be whitelisted/blacklisted only with 'override=True'
    :param func protocol: The client method to use (get, post, etc)
    :param str url: The target url
    :param payload: The data payload to send
    :type payload: dict or None
    :param int valid_status_code: The expected status code when the query is successful
    :param int id_: The IpAddress id to fetch and check the instance
    :param ip_status: The expected final status in case of success
    :return:
    """
    # Whitelisted without override
    payload["override"] = False
    response = protocol(url, data=payload)
    assert response.status_code == 409
    # With override
    payload["override"] = True
    response = protocol(url, data=payload)
    assert response.status_code == valid_status_code
    updated_ip = IpAddress.objects.get(pk=id_)
    assert updated_ip.status == ip_status


def assert_representation_matches_instance(response_data, ip_address):
    """
    Compares a response payload with an IpAddress instance
    :param dict response_data: Output of a "user_representation()"
    :param IpAddress ip_address: User instance from the database
    """
    assert ip_address.id == response_data["id"]
    assert ip_address.ip == response_data["ip"]
    assert ip_address.status == response_data["status"]
    assert ip_address.expires_on == response_data["expires_on"]
    assert ip_address.active == response_data["active"]
    assert ip_address.comment == response_data["comment"]


def assert_unknown_ip(client, protocol, url, payload, admin, user):
    """
    Tests that we get an error if the target IpAddress instance does not exist
    :param APIClient client: The current APIClient used
    :param func protocol: The client method to use (get, post, etc)
    :param str url: The target url
    :param payload: The data payload to send
    :type payload: dict or None
    :param User admin: Any admin user
    :param User user: Any non-admin user
    """
    expected_status_codes = {403, 404}
    # 404 for Admin
    client.force_authenticate(admin)
    response = protocol(url, data=payload)
    assert response.status_code in expected_status_codes
    # 403 for User
    client.logout()
    client.force_authenticate(user)
    response = protocol(url, data=payload)
    assert response.status_code in expected_status_codes


def assert_unique_ip_on_creation(protocol, url, payload, valid_status_code, count):
    """
    Tests that you cannot create the same IP twice
    :param func protocol: The client method to use (get, post, etc)
    :param str url: The target url
    :param payload: The data payload to send
    :type payload: dict or None
    :param int valid_status_code: The expected status code when the query is successful
    :param int count: The current number of instances, before the creation
    """
    # First should succeed
    response = protocol(url, data=payload)
    assert response.status_code == valid_status_code
    assert IpAddress.objects.count() == (count + 1)
    # Second should fail
    response = protocol(url, data=payload)
    assert response.status_code == 400
    assert IpAddress.objects.count() == (count + 1)


def assert_valid_expires_on(protocol, url, payload, valid_status_code, clean_up=False):
    """
    Tests that you must provide a valid date in format and value
    :param func protocol: The client method to use (get, post, etc)
    :param str url: The target url
    :param payload: The data payload to send
    :type payload: dict or None
    :param int valid_status_code: The expected status code when the query is successful
    :param bool clean_up: Whether to clean the recently created instances
    """
    # Invalid dates
    past_date = (date.today() - timedelta(days=1)).strftime("%Y-%m-%d")
    invalid_format_date = (date.today() - timedelta(days=1)).strftime("%Y-%d")
    for date_value in [past_date, invalid_format_date]:
        payload["expires_on"] = date_value
        response = protocol(url, data=payload)
        ActionTestCase().assert_field_has_error(response, "expires_on")
    # Valid date
    raw_date = date.today() + timedelta(days=1)
    formatted_date = raw_date.strftime("%Y-%m-%d")
    for date_value in [raw_date, formatted_date]:
        payload["expires_on"] = date_value
        response = protocol(url, data=payload)
        assert response.status_code == valid_status_code
        if clean_up:
            IpAddress.objects.get(pk=response.data["id"]).delete()


def assert_valid_status(protocol, url, payload, valid_status_code, clean_up=False):
    """
    Tests that you must provide a valid status
    :param func protocol: The client method to use (get, post, etc)
    :param str url: The target url
    :param payload: The data payload to send
    :type payload: dict or None
    :param int valid_status_code: The expected status code when the query is successful
    :param bool clean_up: Whether to clean the recently created instances
    """
    # Invalid statuses
    unknown_integer = 999
    unknown_string = "TEST"
    unsupported_value = 3.3
    for status in [unknown_integer, unknown_string, unsupported_value]:
        payload["status"] = status
        response = protocol(url, data=payload)
        ActionTestCase().assert_field_has_error(response, "status")
    # Valid statuses
    status_as_integer = 1
    status_as_string = "WHITELISTED"
    for status in [status_as_integer, status_as_string]:
        payload["status"] = status
        response = protocol(url, data=payload)
        assert response.status_code == valid_status_code
        if clean_up:
            IpAddress.objects.get(pk=response.data["id"]).delete()
