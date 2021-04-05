"""Permission classes and helpers related to the core API"""

# Personal
from jklib.django.drf.permissions import ImprovedBasePermission

# Application
from security.models import NetworkRule


# --------------------------------------------------------------------------------
# > Permissions
# --------------------------------------------------------------------------------
class IsVerified(ImprovedBasePermission):
    """User must be authenticated but not yet verified"""

    message = "Your account must be verified"

    def has_permission(self, request, view):
        """Returns True if user is logged in and not verified"""
        return bool(
            self.user_is_valid(request)
            and request.user.is_authenticated
            and request.user.is_verified
        )


class IsNotVerified(ImprovedBasePermission):
    """User must be authenticated but not yet verified"""

    message = "Your account must not be verified"

    def has_permission(self, request, view):
        """Returns True if user is logged in and not verified"""
        return bool(
            self.user_is_valid(request)
            and request.user.is_authenticated
            and not request.user.is_verified
        )


class IsBlacklisted(ImprovedBasePermission):
    """Permissions that only allows blacklisted IPs"""

    def has_permission(self, request, view):
        """Returns True if IP is blacklisted"""
        return NetworkRule.is_blacklisted_from_request(request)


class IsNotBlacklisted(ImprovedBasePermission):
    """Permissions that blocks blacklisted IPs"""

    def has_permission(self, request, view):
        """Returns True if IP is not blacklisted"""
        return not NetworkRule.is_blacklisted_from_request(request)


class IsWhitelisted(ImprovedBasePermission):
    """Permissions that only allows whitelisted IPs"""

    def has_permission(self, request, view):
        """Returns True if IP is whitelisted"""
        return NetworkRule.is_whitelisted_from_request(request)


class IsNotWhitelisted(ImprovedBasePermission):
    """Permissions that blocks whitelisted IPs"""

    def has_permission(self, request, view):
        """Returns True if IP is not whitelisted"""
        return not NetworkRule.is_whitelisted_from_request(request)
