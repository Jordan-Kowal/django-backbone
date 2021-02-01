"""TestCase for the 'create' action"""

# Django
from django.contrib.auth.models import User

# Personal
from jklib.django.drf.tests import ActionTestCase

# Local
from ....models import Profile
from ...utils import assert_user_email_was_sent
from ._shared import USER_SERVICE_URL, assert_user_representation_matches_instance


# --------------------------------------------------------------------------------
# > TestCase
# --------------------------------------------------------------------------------
class TestCreateUser(ActionTestCase):
    """TestCase for the 'create' action"""

    required_fields = ["email", "password", "confirm_password"]
    service_base_url = f"{USER_SERVICE_URL}/"
    success_code = 201

    # ----------------------------------------
    # Behavior
    # ----------------------------------------
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

    # ----------------------------------------
    # Tests
    # ----------------------------------------
    def test_permissions(self):
        """Tests that this service is restricted to unauthenticated users"""
        self.create_user(authenticate=True)
        assert User.objects.count() == 1
        # Authenticated is 403
        response = self.client.post(self.service_base_url, data=self.payload)
        assert response.status_code == 403
        assert User.objects.count() == 1
        # Unauthenticated is 201
        self.client.logout()
        response = self.client.post(self.service_base_url, data=self.payload)
        assert response.status_code == self.success_code
        assert User.objects.count() == 2

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

    def test_name_trimming(self):
        """Tests that the firstname and lastname are trimmed"""
        self.payload["first_name"] = " First Name"
        self.payload["last_name"] = "Last Name "
        response = self.client.post(self.service_base_url, data=self.payload)
        assert response.status_code == self.success_code
        assert User.objects.count() == 1
        user = User.objects.first()
        assert user.first_name == self.payload["first_name"].strip()
        assert user.last_name == self.payload["last_name"].strip()

    def test_create_success(self):
        """Tests that you can successfully create a user"""
        # Successful create
        response = self.client.post(self.service_base_url, data=self.payload)
        assert response.status_code == self.success_code
        assert User.objects.count() == 1
        # Check content
        user = User.objects.first()
        assert_user_representation_matches_instance(response.data, user)
        # Check the email was sent
        subject = (
            Profile.EmailTemplate.WELCOME.subject
            if user.profile.is_verified
            else Profile.EmailTemplate.VERIFY_EMAIL.subject
        )
        assert_user_email_was_sent(user, subject)
