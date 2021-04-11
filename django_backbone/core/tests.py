"""Utilities for testing"""

# Personal
from jklib.django.drf.tests import ActionTestCase

# Application
from users.factories import AdminFactory, UserFactory


# --------------------------------------------------------------------------------
# > Helpers
# --------------------------------------------------------------------------------
class BaseActionTestCase(ActionTestCase):
    """Extends the ActionTestCase to provide utilities like permission-check shortcuts"""

    def assert_admin_permissions(self, url, data=None, user=None, admin=None):
        """
        Checks that the service is only available to admin users
        :param TestCase self: The current TestCase instance
        :param str url: The target url
        :param dict data: The data to pass to the request
        :param User user: An existing non-admin user
        :param User admin: An existing admin user
        """
        if user is None:
            user = UserFactory()
        if admin is None:
            admin = AdminFactory()
        # 401 Not authenticated
        self.api_client.logout()
        response = self.http_method(url, data=data)
        assert response.status_code == 401
        # 403 Not admin
        self.api_client.force_authenticate(user)
        response = self.http_method(url, data=data)
        assert response.status_code == 403
        # 201 Admin
        self.api_client.logout()
        self.api_client.force_authenticate(admin)
        response = self.http_method(url, data=data)
        assert response.status_code == self.success_code

    def assert_anyone_permissions(self, url, data=None):
        """
        Checks anyone can use this service
        :param str url: URL of the endpoint
        :param dict data: The data for the request
        """
        user = UserFactory()
        admin = AdminFactory()
        # Logged out
        self.api_client.logout()
        response = self.http_method(url, data=data)
        assert response.status_code == self.success_code
        # User
        self.api_client.force_authenticate(user)
        response = self.http_method(url, data=data)
        assert response.status_code == self.success_code
        # User
        self.api_client.logout()
        self.api_client.force_authenticate(admin)
        response = self.http_method(url, data=data)
        assert response.status_code == self.success_code

    def assert_not_authenticated_permissions(
        self, url, data=None, user=None, admin=None
    ):
        """
        Checks permissions are 'Not authenticated' only
        :param str url: URL of the endpoint
        :param dict data: The data for the request
        :param User user: An existing non-admin user
        :param User admin: An existing admin user
        """
        if user is None:
            user = UserFactory()
        if admin is None:
            admin = AdminFactory()
        for user_instance in [user, admin]:
            self.api_client.force_authenticate(user_instance)
            response = self.http_method(url, data=data)
            assert response.status_code == 403
            self.api_client.logout()
        response = self.http_method(url, data=data)
        assert response.status_code == self.success_code

    def assert_owner_permissions(self, url, owner, not_owner, data=None):
        """
        Checks only the owner can reach the object
        :param str url: URL of the endpoint
        :param User owner: The owner of the object
        :param User not_owner: A user that is not the owner
        :param dict data: The data for the request
        """
        # Logged out
        self.api_client.logout()
        response = self.http_method(url, data=data)
        assert response.status_code == 401
        # Not owner
        self.api_client.force_authenticate(not_owner)
        response = self.http_method(url, data=data)
        assert response.status_code == 403
        # Owner
        self.api_client.force_authenticate(owner)
        response = self.http_method(url, data=data)
        assert response.status_code == self.success_code
