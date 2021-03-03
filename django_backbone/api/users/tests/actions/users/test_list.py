"""TestCase for the 'list' action"""

# Django
from django.contrib.auth.models import User

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
    # Tests
    # ----------------------------------------
    def test_permissions(self):
        """Tests that unauthenticated users and non-admin users can't access the service"""
        # 401 Unauthenticated
        response = self.client.get(self.service_base_url)
        assert response.status_code == 401
        # User is 403 Unauthorized
        self.create_user(authenticate=True)
        response = self.client.get(self.service_base_url)
        assert response.status_code == 403
        # Admin is 200 OK
        self.client.logout()
        self.create_admin_user(authenticate=True)
        response = self.client.get(self.service_base_url)
        assert response.status_code == 200

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
