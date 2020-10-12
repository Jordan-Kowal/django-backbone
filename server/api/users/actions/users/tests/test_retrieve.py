"""TestCase for the 'retrieve' action"""

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
class TestRetrieveUser(ActionTestCase):
    """TestCase for the 'retrieve' action"""

    service_base_url = f"{USER_SERVICE_URL}/"

    # ----------------------------------------
    # Behavior
    # ----------------------------------------
    @classmethod
    def setUpClass(cls):
        """Sets up the API client"""
        cls.client = APIClient()

    def setUp(self):
        """Not implemented"""
        pass

    def tearDown(self):
        """Not implemented"""
        pass

    @classmethod
    def tearDownClass(cls):
        """Not implemented"""
        pass

    # ----------------------------------------
    # Tests
    # ----------------------------------------
    def test_permissions(self):
        """Tests only admin or object owners can call this service"""
        # 401 Unauthenticated
        first_user = self.create_user(authenticate=False)
        assert first_user.id == 1
        first_url = self.detail_url(first_user.id)
        response = self.client.get(first_url)
        assert response.status_code == 401
        # 403 Not owner
        second_user = self.create_user(authenticate=True)
        assert second_user.id == 2
        response = self.client.get(first_url)
        assert response.status_code == 403
        # 200 Owner
        second_url = self.detail_url(second_user.id)
        response = self.client.get(second_url)
        assert response.status_code == 200
        # 200 Admin
        self.client.logout()
        self.create_admin_user(authenticate=True)
        response = self.client.get(second_url)
        assert response.status_code == 200

    def test_unknown_user(self):
        """Tests that users cannot fetch a non-existing resource"""
        admin = self.create_admin_user()
        user = self.create_user()
        assert admin.id == 1
        assert user.id == 2
        assert User.objects.count() == 2
        url = self.detail_url(3)
        # Admin should get 404
        self.client.force_authenticate(admin)
        response = self.client.get(url)
        assert response.status_code == 404
        self.client.logout()
        # User should get 404
        self.client.force_authenticate(user)
        response = self.client.get(url)
        assert response.status_code == 404

    def test_retrieve_success(self):
        """Tests that the owner can successfully fetch his own data"""
        user = self.create_user(authenticate=True)
        assert user.id == 1
        url = self.detail_url(user.id)
        response = self.client.get(url)
        assert response.status_code == 200
        assert_user_representation_matches_instance(response.data, user)
