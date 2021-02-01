"""TestCase for the 'perform_password_reset' action"""

# Django
from django.contrib.auth.models import User

# Personal
from jklib.django.drf.tests import ActionTestCase

# Local
from ....models import Profile, Token
from ...utils import assert_user_email_was_sent
from ._shared import USER_SERVICE_URL


# --------------------------------------------------------------------------------
# > TestCase
# --------------------------------------------------------------------------------
class TestPerformPasswordReset(ActionTestCase):
    """TestCase for the 'perform_password_reset' action"""

    service_base_url = f"{USER_SERVICE_URL}/perform_password_reset/"
    required_fields = [
        "new_password",
        "confirm_new_password",
        "token",
    ]

    # ----------------------------------------
    # Behavior
    # ----------------------------------------
    @classmethod
    def setUpClass(cls):
        """Sets up the token type"""
        cls.token_type, _ = Profile.RESET_TOKEN
        super(TestPerformPasswordReset, cls).setUpClass()

    def setUp(self):
        """Creates 1 basic user, 1 reset token for this user, and a valid payload for the service"""
        # User with specific password
        self.password = self.generate_random_string(20)
        self.user = self.create_user(password=self.password)
        # Generating and storing a token
        token_instance, token_value = Token.create_new_token(
            self.user, self.token_type, 300
        )
        self.token_instance = token_instance
        self.token_value = token_value
        # Preparing a valid payload
        new_password = self.generate_random_string(20)
        self.payload = {
            "new_password": new_password,
            "confirm_new_password": new_password,
            "token": token_value,
        }

    # ----------------------------------------
    # Tests
    # ----------------------------------------
    def test_permissions(self):
        """Tests that the service can be accessed only if disconnected"""
        # 403 Unauthorized
        self.client.force_authenticate(self.user)
        response = self.client.post(self.service_base_url, self.payload)
        assert response.status_code == 403
        # 204 OK
        self.client.logout()
        response = self.client.post(self.service_base_url, self.payload)
        assert response.status_code == 204

    def test_required_fields(self):
        """Tests that required fields are truly required"""
        self.assert_fields_are_required(
            self.client.post, self.service_base_url, self.payload
        )

    def test_password_strength(self):
        """Tests that the new password is strong enough"""
        self.payload["new_password"] = "weak"
        self.payload["confirm_new_password"] = "weak"
        response = self.client.post(self.service_base_url, self.payload)
        self.assert_field_has_error(response, "new_password")

    def test_confirm_password_matches_password(self):
        """Tests that the new password has been typed correctly twice"""
        self.payload["confirm_new_password"] = self.generate_random_string(10)
        response = self.client.post(self.service_base_url, self.payload)
        self.assert_field_has_error(response, "confirm_new_password")

    def test_invalid_token(self):
        """Tests that you must provide a token with the right value and type"""
        # Unknown token
        self.payload["token"] = "unknown token value"
        response = self.client.post(self.service_base_url, self.payload)
        self.assert_field_has_error(response, "token")
        # Token exists but wrong type
        _, token_with_wrong_type = Token.create_new_token(self.user, "invalid", 300)
        self.payload["token"] = token_with_wrong_type
        response = self.client.post(self.service_base_url, self.payload)
        self.assert_field_has_error(response, "token")

    def test_already_used_token(self):
        """Tests that you must provide a token that can be used"""
        self.token_instance.consume_token()
        response = self.client.post(self.service_base_url, self.payload)
        self.assert_field_has_error(response, "token")

    def test_success(self):
        """Tests that you can successfully change your password, and the token gets consumed"""
        # Successful request
        response = self.client.post(self.service_base_url, self.payload)
        assert response.status_code == 204
        # Checking that only the new password now works
        user = User.objects.get(id=self.user.id)
        assert not user.check_password(self.password)
        assert user.check_password(self.payload["new_password"])
        # Checking that the update email has been sent
        subject = Profile.EmailTemplate.PASSWORD_UPDATED.subject
        assert_user_email_was_sent(user, subject)
        # Trying again should fail
        response = self.client.post(self.service_base_url, self.payload)
        self.assert_field_has_error(response, "token")
