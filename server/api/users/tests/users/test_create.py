"""TestCase for the 'create' action"""

# Django
from django.contrib.auth.models import User
from rest_framework.test import APIClient

# Personal
from jklib.django.drf.tests import ActionTestCase

# Local
from ...models import Profile
from ._shared import USER_SERVICE_URL, assert_user_representation_matches_instance


# --------------------------------------------------------------------------------
# > TestCase
# --------------------------------------------------------------------------------
class TestCreateUser(ActionTestCase):
    """TestCase for the 'create' action"""

    required_fields = ["email", "password", "confirm_password"]
    service_base_url = f"{USER_SERVICE_URL}/"

    # ----------------------------------------
    # Behavior
    # ----------------------------------------
    @classmethod
    def setUpClass(cls):
        """Sets up the API client"""
        cls.client = APIClient()

    def setUp(self):
        """Stores a default user and creates a valid payload"""
        self.default_user = self.generate_random_user_data()
        self.payload = {
            "email": self.default_user["email"],
            "first_name": self.default_user["first_name"],
            "last_name": self.default_user["last_name"],
            "password": self.default_user["password"],
            "confirm_password": self.default_user["password"],
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
        """Tests that this service is restricted to unauthenticated users"""
        self.create_user(authenticate=True)
        response = self.client.post(self.service_base_url, data=self.payload)
        assert response.status_code == 403
        assert User.objects.count() == 1

    def test_required_fields(self):
        """Tests that required fields are indeed required"""
        self.assert_fields_are_required(
            handler=self.client.post,
            url=self.service_base_url,
            valid_payload=self.payload,
        )

    def test_password_strength(self):
        """Tests that the password cannot be too weak"""
        self.payload["password"] = "test"
        self.payload["confirm_password"] = "test"
        response = self.client.post(self.service_base_url, data=self.payload)
        self.assert_field_has_error(response, "password")

    def test_matching_passwords(self):
        """Tests that confirm_password must match password"""
        self.payload["password"] = "Qjjs8n!6qLbY61@Qjd"
        self.payload["confirm_password"] = "DifferentValue"
        response = self.client.post(self.service_base_url, data=self.payload)
        self.assert_field_has_error(response, "confirm_password")

    def test_email_format(self):
        """Tests that the email must be an email format"""
        # Almost an email
        self.payload["email"] = "invalid@email"
        response = self.client.post(self.service_base_url, data=self.payload)
        self.assert_field_has_error(response, "email")
        # Totally not an email
        self.payload["email"] = 33
        response = self.client.post(self.service_base_url, data=self.payload)
        self.assert_field_has_error(response, "email")

    def test_unique_email(self):
        """Tests that the email must be unique"""
        user = self.create_user()
        self.payload["email"] = user.email
        response = self.client.post(self.service_base_url, data=self.payload)
        self.assert_field_has_error(response, "email")
        assert User.objects.count() == 1

    def test_create_success(self):
        """Tests that you can successfully create a user"""
        # Successful create
        response = self.client.post(self.service_base_url, data=self.payload)
        assert response.status_code == 201
        assert User.objects.count() == 1
        # Check content
        user = User.objects.first()
        assert_user_representation_matches_instance(response.data, user)
        # Check the email was sent
        if user.profile.is_verified:
            subject = Profile.EMAILS["welcome"]["subject"]
        else:
            subject = Profile.EMAILS["verification_email"]["subject"]
        self.assert_email_was_sent(subject)
