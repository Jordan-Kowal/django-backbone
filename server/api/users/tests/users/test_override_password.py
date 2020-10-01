"""TestCase for the 'override_password' action"""

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
class TestOverridePassword(ActionTestCase):
    """TestCase for the 'override_password' action"""

    service_base_url = f"{USER_SERVICE_URL}/"
    service_extra_url = "override_password/"
    required_fields = ["password", "confirm_password"]

    # ----------------------------------------
    # Behavior
    # ----------------------------------------
    @classmethod
    def setUpClass(cls):
        """Sets up the API client"""
        cls.client = APIClient()

    def setUp(self):
        """Generates 1 user and 1 admin with predefined passwords and 1 valid payload"""
        # Admin
        self.admin_password = self.generate_random_string(20)
        self.admin = self.create_admin_user(password=self.admin_password)
        self.admin_url = self.detail_url(self.admin.id)
        # User
        self.user_password = self.generate_random_string(20)
        self.user = self.create_user(password=self.user_password)
        self.user_url = self.detail_url(self.user.id)
        # Payload
        self.password = self.generate_random_string(20)
        self.payload = {
            "password": self.password,
            "confirm_password": self.password,
        }

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
        """Tests that only admins can use this service"""
        # 401 Logged out
        response = self.client.post(self.user_url, self.payload)
        assert response.status_code == 401
        # 403 Unauthorized (not an admin)
        self.client.force_authenticate(self.user)
        response = self.client.post(self.user_url, self.payload)
        assert response.status_code == 403
        # 204 OK (admin on user)
        self.client.logout()
        self.client.force_authenticate(self.admin)
        response = self.client.post(self.user_url, self.payload)
        assert response.status_code == 204
        # 204 OK (admin on self)
        response = self.client.post(self.admin_url, self.payload)
        assert response.status_code == 204

    def test_required_fields(self):
        """Tests that the required fields are truly required"""
        self.client.force_authenticate(self.admin)
        self.assert_fields_are_required(self.client.post, self.user_url, self.payload)

    def test_password_strength(self):
        """Tests that the password is strong enough"""
        self.client.force_authenticate(self.admin)
        self.payload["password"] = "weak"
        self.payload["password"] = "weak"
        response = self.client.post(self.user_url, self.payload)
        self.assert_field_has_error(response, "password")

    def test_confirm_password_matches_password(self):
        """Tests that the password has been typed correctly twice"""
        self.client.force_authenticate(self.admin)
        self.payload["confirm_password"] = "different"
        response = self.client.post(self.user_url, self.payload)
        self.assert_field_has_error(response, "confirm_password")

    def test_override_password_success(self):
        """Tests that overriding the password actually works"""
        # Performing the request
        self.client.force_authenticate(self.admin)
        response = self.client.post(self.user_url, self.payload)
        # Checking that only the new password now works
        user = User.objects.get(id=self.user.id)
        assert response.status_code == 204
        assert not user.check_password(self.user_password)
        assert user.check_password(self.password)
