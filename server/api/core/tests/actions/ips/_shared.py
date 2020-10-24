"""Shared constants, functions, and classes for our IP service tests"""

# Built-in
from datetime import date, timedelta

# Application
from api.core.models import IpAddress

# --------------------------------------------------------------------------------
# > Constants
# --------------------------------------------------------------------------------
SERVICE_URL = "/api/ips"
DEFAULT_VALUES = {
    "ip": "127.0.0.1",
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
