"""TestCase for the 'verify' action"""

# Django
from django.contrib.auth.models import User

# Personal
from jklib.django.drf.tests import ActionTestCase

# Local
from ....models import Profile, Token
from ._shared import USER_SERVICE_URL


# --------------------------------------------------------------------------------
# > TestCase
# --------------------------------------------------------------------------------
class TestVerifyUser(ActionTestCase):
    """TestCase for the 'verify' action"""

    service_base_url = f"{USER_SERVICE_URL}/verify/"

    # ----------------------------------------
    # Behavior
    # ----------------------------------------
    @classmethod
    def setUpClass(cls):
        """Sets up the token type"""
        cls.token_type, _ = Profile.VERIFY_TOKEN
        super(TestVerifyUser, cls).setUpClass()

    def setUp(self):
        """Creates 1 basic user"""
        self.user = self.create_user()

    # ----------------------------------------
    # Tests
    # ----------------------------------------
    def test_permissions(self):
        """Service is available for everyone"""
        pass

    def test_required_fields(self):
        """Tests that the 'token' field is required"""
        payload = {"token": None}
        response = self.client.post(self.service_base_url, payload)
        self.assert_field_has_error(response, "token")

    def test_invalid_token(self):
        """Tests that you cannot provide an invalid token or token type"""
        _, invalid_token = Token.create_new_token(self.user, "invalid", 300)
        # Unknown token
        payload = {"token": "unknown token"}
        response = self.client.post(self.service_base_url, payload)
        self.assert_field_has_error(response, "token")
        # Token exists but wrong type
        payload = {"token": invalid_token}
        response = self.client.post(self.service_base_url, payload)
        self.assert_field_has_error(response, "token")

    def test_already_used_token(self):
        """Tests that you cannot use an already-used token"""
        token_instance, token_value = Token.create_new_token(
            self.user, self.token_type, 300
        )
        token_instance.consume_token()
        payload = {"token": token_value}
        response = self.client.post(self.service_base_url, payload)
        self.assert_field_has_error(response, "token")

    def test_success(self):
        """Tests that providing a valid token changes the profile to verified"""
        # Successful request
        _, token_value = Token.create_new_token(self.user, self.token_type, 300)
        payload = {"token": token_value}
        response = self.client.post(self.service_base_url, payload)
        assert response.status_code == 204
        user_instance = User.objects.get(id=self.user.id)
        assert user_instance.profile.is_verified
        # Welcome email was sent
        subject = Profile.EmailTemplate.WELCOME.subject
        self.assert_email_was_sent(subject)
        # Trying again should fail
        response = self.client.post(self.service_base_url, payload)
        self.assert_field_has_error(response, "token")
