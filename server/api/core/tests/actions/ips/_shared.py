"""Shared constants, functions, and classes for our IP service tests"""


# --------------------------------------------------------------------------------
# > Constants
# --------------------------------------------------------------------------------
SERVICE_URL = "/api/ips"


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
