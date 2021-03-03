"""TestCase for the 'request_password_reset' action"""

# Built-in
from time import sleep

# Django
from django.contrib.auth.models import User
from django.core import mail

# Personal
from jklib.django.drf.tests import ActionTestCase

# Local
from ....models import Profile, Token
from ...utils import assert_user_email_was_sent
from ._shared import USER_SERVICE_URL


# --------------------------------------------------------------------------------
# > TestCase
# --------------------------------------------------------------------------------
class TestRequestPasswordReset(ActionTestCase):
    """TestCase for the 'request_password_reset' action"""

    service_base_url = f"{USER_SERVICE_URL}/request_password_reset/"
    required_fields = ["email"]

    # ----------------------------------------
    # Behavior
    # ----------------------------------------
    @classmethod
    def setUpClass(cls):
        """Sets up the token type"""
        cls.token_type, _ = Profile.RESET_TOKEN
        super(TestRequestPasswordReset, cls).setUpClass()

    def setUp(self):
        """Creates 1 basic user"""
        self.user = self.create_user()
        self.payload = {"email": self.user.email}

    # ----------------------------------------
    # Tests
    # ----------------------------------------
    def test_permissions(self):
        """Tests that the service can be accessed only if disconnected"""
        # 403 Unauthorized
        self.client.force_authenticate(self.user)
        response = self.client.post(self.service_base_url, self.payload)
        assert response.status_code == 403
        # 202 OK
        self.client.logout()
        response = self.client.post(self.service_base_url, self.payload)
        assert response.status_code == 202

    def test_required_fields(self):
        """Tests that 'email' is a required field"""
        self.assert_fields_are_required(
            self.client.post, self.service_base_url, self.payload
        )

    def test_email_format(self):
        """Tests that the email field must be an actual email"""
        # Almost an email
        self.payload["email"] = "invalid@email"
        response = self.client.post(self.service_base_url, self.payload)
        self.assert_field_has_error(response, "email")
        # Totally not an email
        self.payload["email"] = 33
        response = self.client.post(self.service_base_url, self.payload)
        self.assert_field_has_error(response, "email")

    def test_success_with_unknown_email(self):
        """Tests a success with a valid email, meaning a token was created and an email was sent"""
        # Successful request
        response = self.client.post(self.service_base_url, self.payload)
        assert response.status_code == 202
        # Token exists
        user_tokens = Token.objects.filter(user=self.user, type=self.token_type)
        token = user_tokens[0]
        assert len(user_tokens) == 1
        assert token.can_be_used
        # Checks the email was sent (asynchronously)
        subject = Profile.EmailTemplate.REQUEST_PASSWORD_RESET.subject
        assert_user_email_was_sent(self.user, subject)

    def test_success_with_known_email(self):
        """Tests a success without a valid email, meaning no token was created and no email was sent"""
        # Make sure no user has our email
        self.payload["email"] = "invalid-email@invalid-domain.com"
        users = User.objects.filter(email=self.payload["email"])
        assert len(users) == 0
        # Successful request
        response = self.client.post(self.service_base_url, self.payload)
        assert response.status_code == 202
        # No tokens
        tokens = Token.objects.filter(type=self.token_type)
        assert len(tokens) == 0
        # No mail
        sleep(0.2)
        assert len(mail.outbox) == 0
