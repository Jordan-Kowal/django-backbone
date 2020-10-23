"""TestCase for the 'destroy' action"""


# Django
from django.contrib.auth.models import User
from rest_framework.test import APIClient

# Personal
from jklib.django.drf.tests import ActionTestCase

# Local
from ._shared import USER_SERVICE_URL


# --------------------------------------------------------------------------------
# > TestCase
# --------------------------------------------------------------------------------
class TestDestroyUser(ActionTestCase):
    """TestCase for the 'destroy' action"""

    service_base_url = f"{USER_SERVICE_URL}/"

    # ----------------------------------------
    # Behavior
    # ----------------------------------------
    @classmethod
    def setUpClass(cls):
        """Sets up the API client"""
        cls.client = APIClient()

    def setUp(self):
        """Creates 2 users (1 admin and 1 normal)"""
        self.admin = self.create_admin_user()
        self.admin_detail_url = self.detail_url(self.admin.id)
        self.user = self.create_user()
        self.user_detail_url = self.detail_url(self.user.id)

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
        """Tests that access is restricted to owner or admin"""
        # 401 Unauthenticated
        response = self.client.delete(self.admin_detail_url)
        assert response.status_code == 401
        # 403 Not owner
        self.client.force_authenticate(self.user)
        response = self.client.delete(self.admin_detail_url)
        assert response.status_code == 403
        # 204 Owner
        response = self.client.delete(self.user_detail_url)
        assert response.status_code == 204
        # 204 Admin
        self.client.logout()
        third_user = self.create_user()
        third_user_detail_url = self.detail_url(third_user.id)
        self.client.force_authenticate(self.admin)
        response = self.client.delete(third_user_detail_url)
        assert response.status_code == 204

    def test_unknown_user(self):
        """Tests that you can't delete an unknown user"""
        invalid_url = self.detail_url(3)
        # Admin can't find it
        self.client.force_authenticate(self.admin)
        response = self.client.delete(invalid_url)
        assert response.status_code == 404
        # User can't find it
        self.client.logout()
        self.client.force_authenticate(self.user)
        response = self.client.delete(invalid_url)
        assert response.status_code == 404

    def test_destroy_success(self):
        """Tests that we successfully deleted our user"""
        # Deletes the user
        self.client.force_authenticate(self.user)
        response = self.client.delete(self.user_detail_url)
        assert response.status_code == 204
        assert User.objects.count() == 1
        self.client.logout()
        # URL should now return a 404
        self.client.force_authenticate(self.admin)
        response = self.client.delete(self.user_detail_url)
        assert response.status_code == 404
