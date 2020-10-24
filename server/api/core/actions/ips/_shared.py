"""
Reusable classes, functions and variables available for all our core ip services
Split into the following categories:
    Representation
    Status Management
    Validators
"""

# Built-in
from datetime import date

# Django
from rest_framework.serializers import ValidationError

# Application
from api.core.models import IpAddress


# --------------------------------------------------------------------------------
# > Representation
# --------------------------------------------------------------------------------
def ip_address_representation(ip_address):
    """
    Formats an IpAddress model into a dict
    :param IpAddress ip_address: The IpAddress model to return
    :return: Dict of our IpAddress data
    :rtype: dict
    """
    return {
        "id": ip_address.id,
        "ip": ip_address.ip,
        "status": ip_address.status,
        "expires_on": ip_address.expires_on,
        "active": ip_address.active,
        "comment": ip_address.comment,
    }


# --------------------------------------------------------------------------------
# > Status management
# --------------------------------------------------------------------------------
STATUS_TO_ENUM = {
    1: IpAddress.IpStatus.NONE,
    2: IpAddress.IpStatus.WHITELISTED,
    3: IpAddress.IpStatus.BLACKLISTED,
    "NONE": IpAddress.IpStatus.NONE,
    "WHITELISTED": IpAddress.IpStatus.WHITELISTED,
    "BLACKLISTED": IpAddress.IpStatus.BLACKLISTED,
}

STATUS_CHOICES = list(STATUS_TO_ENUM.keys())


# --------------------------------------------------------------------------------
# > Validators
# --------------------------------------------------------------------------------
def validate_expires_on(expiration_date):
    """
    Checks that the expiration date is in the future
    :param date expiration_date: The provided datetime value
    :return: The untouched expiration date
    :rtype: date
    """
    if expiration_date < date.today():
        raise ValidationError("Expiration date cannot be in the past")
    return expiration_date


def validate_status(status):
    """
    Converts the status from int/str to a valid enum
    :param status: The provided status for the IpAddress
    :type status: str or int
    :return: The status converted to its enum integer value
    :rtype: int
    """
    status_enum = STATUS_TO_ENUM.get(status, None)
    if status_enum is None:
        raise ValidationError("Provided 'status' is invalid")
    return status_enum
