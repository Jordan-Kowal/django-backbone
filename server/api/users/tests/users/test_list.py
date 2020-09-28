"""TestCase for the 'list' action"""

# Django
from django.contrib.auth.models import User
from rest_framework.test import APIClient

# Personal
from jklib.django.drf.tests import ActionTestCase

# Local
from ._shared import USER_SERVICE_URL, assert_user_representation_matches_instance


# --------------------------------------------------------------------------------
# > TestCase
# --------------------------------------------------------------------------------
class TestListUsers(ActionTestCase):
    """TestCase for the 'list' action"""

    service_base_url = f"{USER_SERVICE_URL}/"

    # ----------------------------------------
    # Behavior
    # ----------------------------------------
    @classmethod
    def setUpClass(cls):
        """Sets up the API client"""
        cls.client = APIClient()

    def setUp(self):
        """Stores a copy of the default user data"""
        pass

    def teardown(self):
        """Removes all users from the database and logs out the current client"""
        User.objects.all().delete()
        self.client.logout()

    @classmethod
    def tearDownClass(cls):
        """Not implemented"""
        pass

    # ----------------------------------------
    # Tests
    # ----------------------------------------
    def test_permissions(self):
        """Tests that unauthenticated users and non-admin users can't access the service"""
        # Logged out
        response = self.client.get(self.service_base_url)
        assert response.status_code == 401
        # Unauthorized
        self.create_user(authenticate=True)
        response = self.client.get(self.service_base_url)
        assert response.status_code == 403

    def test_list_one_user(self):
        """Tests that the service returns 1 user properly"""
        self.create_admin_user(authenticate=True)
        response = self.client.get(self.service_base_url)
        assert response.status_code == 200
        assert len(response.data) == 1
        self._assert_database_matches_user_representation(response.data)

    def test_list_several_users(self):
        """Tests that the service returns several users properly"""
        self.create_admin_user(authenticate=True)
        self.create_user()
        response = self.client.get(self.service_base_url)
        assert response.status_code == 200
        assert len(response.data) == 2
        self._assert_database_matches_user_representation(response.data)

    # ----------------------------------------
    # Private
    # ----------------------------------------
    @staticmethod
    def _assert_database_matches_user_representation(response_data):
        """Checks that the provided user data matches"""
        users = User.objects.all().order_by("id")
        response_data.sort(key=lambda x: x["id"])
        assert len(users) == len(response_data)
        for i in range(len(users)):
            user_instance = users[i]
            user_json = response_data[i]
            assert_user_representation_matches_instance(user_json, user_instance)
