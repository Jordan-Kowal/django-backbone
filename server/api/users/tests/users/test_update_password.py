"""TestCase for the 'update_password' action"""

# Django
from django.contrib.auth.models import User
from rest_framework.test import APIClient

# Personal
from jklib.django.drf.tests import ActionTestCase

# Local
from ...models import Profile
from ._shared import USER_SERVICE_URL


# --------------------------------------------------------------------------------
# > TestCase
# --------------------------------------------------------------------------------
class TestUpdatePassword(ActionTestCase):
    """TestCase for the 'update_password' action"""

    service_url = f"{USER_SERVICE_URL}/self/update_password/"
    required_fields = ["current_password", "new_password", "confirm_new_password"]

    # ----------------------------------------
    # Behavior
    # ----------------------------------------
    @classmethod
    def setUpClass(cls):
        """Sets up the API client"""
        cls.client = APIClient()

    def setUp(self):
        """Generates a password and creates 1 basic user"""
        self.password = self.generate_random_string(20)
        self.user = self.create_user(password=self.password)
        self.generate_valid_payload()

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
        """Tests that you must be authenticated to use this service"""
        # 401 Unauthorized
        response = self.client.post(self.service_url, self.payload)
        assert response.status_code == 401
        # 204 Ok
        self.client.force_authenticate(self.user)
        response = self.client.post(self.service_url, self.payload)
        assert response.status_code == 204

    def test_required_fields(self):
        """Tests that the required fields are truly required"""
        self.client.force_authenticate(self.user)
        self.assert_fields_are_required(
            self.client.post, self.service_url, self.payload
        )

    def test_current_password_must_be_valid(self):
        """Tests that the user provided the right password"""
        self.client.force_authenticate(self.user)
        self.payload["current_password"] = "Invalid password"
        response = self.client.post(self.service_url, self.payload)
        self.assert_field_has_error(response, "current_password")

    def test_new_password_strength(self):
        """Tests that the new password is strong enough"""
        self.client.force_authenticate(self.user)
        self.payload["new_password"] = "weak"
        self.payload["confirm_new_password"] = "weak"
        response = self.client.post(self.service_url, self.payload)
        self.assert_field_has_error(response, "new_password")

    def test_confirm_password_matches_new_password(self):
        """Tests that the new password has been typed correctly twice"""
        self.client.force_authenticate(self.user)
        self.payload["confirm_new_password"] = "different"
        response = self.client.post(self.service_url, self.payload)
        self.assert_field_has_error(response, "confirm_new_password")

    def test_update_password_success(self):
        """Tests that updating the password truly changes the password"""
        # Performing the request
        self.client.force_authenticate(self.user)
        response = self.client.post(self.service_url, self.payload)
        assert response.status_code == 204
        # Checking that only the new password now works
        previous_password = self.payload["current_password"]
        new_password = self.payload["new_password"]
        assert not self.user.check_password(previous_password)
        assert self.user.check_password(new_password)
        # Checking notification email was sent
        subject = Profile.EMAILS["password_update"]["subject"]
        self.assert_email_was_sent(subject)

    # ----------------------------------------
    # Private
    # ----------------------------------------
    def generate_valid_payload(self):
        """Generates a valid payload for the service request"""
        new_password = self.generate_random_string(20)
        self.payload = {
            "current_password": self.password,
            "new_password": new_password,
            "confirm_new_password": new_password,
        }
