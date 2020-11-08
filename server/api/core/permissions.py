"""Permission classes and helpers related to the core API"""

# Personal
from jklib.django.drf.permissions import ImprovedBasePermission

# Local
from .models import IpAddress


# --------------------------------------------------------------------------------
# > Permissions
# --------------------------------------------------------------------------------
class IsBlacklisted(ImprovedBasePermission):
    """Permissions that only allows blacklisted IPs"""

    def has_permission(self, request, view):
        """Returns True if IP is blacklisted"""
        return IpAddress.is_blacklisted_from_request(request)


class IsNotBlacklisted(ImprovedBasePermission):
    """Permissions that blocks blacklisted IPs"""

    def has_permission(self, request, view):
        """Returns True if IP is not blacklisted"""
        return not IpAddress.is_blacklisted_from_request(request)


class IsWhitelisted(ImprovedBasePermission):
    """Permissions that only allows whitelisted IPs"""

    def has_permission(self, request, view):
        """Returns True if IP is whitelisted"""
        return IpAddress.is_whitelisted_from_request(request)


class IsNotWhitelisted(ImprovedBasePermission):
    """Permissions that blocks whitelisted IPs"""

    def has_permission(self, request, view):
        """Returns True if IP is not whitelisted"""
        return not IpAddress.is_whitelisted_from_request(request)
