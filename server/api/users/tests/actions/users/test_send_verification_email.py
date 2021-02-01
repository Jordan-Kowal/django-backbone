"""TestCase for the 'send_verification_email' action"""

# Personal
from jklib.django.drf.tests import ActionTestCase

# Local
from ....models import Profile, Token
from ...utils import assert_user_email_was_sent
from ._shared import USER_SERVICE_URL


# --------------------------------------------------------------------------------
# > TestCase
# --------------------------------------------------------------------------------
class TestSendVerificationEmail(ActionTestCase):
    """TestCase for the 'send_verification_email' action"""

    service_base_url = f"{USER_SERVICE_URL}/"
    service_extra_url = "send_verification_email/"

    # ----------------------------------------
    # Behavior
    # ----------------------------------------
    @classmethod
    def setUpClass(cls):
        """Sets up the token type"""
        cls.token_type, _ = Profile.VERIFY_TOKEN
        super(TestSendVerificationEmail, cls).setUpClass()

    def setUp(self):
        """Creates 1 basic user"""
        self.user = self.create_user()
        self.user_url = self.detail_url(self.user.id)

    # ----------------------------------------
    # Tests
    # ----------------------------------------
    def test_permissions(self):
        """Tests that you must be authenticated to use this service"""
        # Create additional users
        admin = self.create_admin_user()
        other_user = self.create_user()
        other_user_url = self.detail_url(other_user.id)
        # 401 Unauthorized
        response = self.client.post(self.user_url)
        assert response.status_code == 401
        # 403 Unauthorized (user and not owner)
        self.client.force_authenticate(self.user)
        response = self.client.post(other_user_url)
        assert response.status_code == 403
        # 204 Ok (user and owner)
        response = self.client.post(self.user_url)
        assert response.status_code == 204
        # 204 Ok (admin but not owner)
        self.client.logout()
        self.client.force_authenticate(admin)
        response = self.client.post(self.user_url)
        assert response.status_code == 204

    def test_success(self):
        """Tests that the verification token is created and the email is sent"""
        self.client.force_authenticate(self.user)
        # Response 204
        response = self.client.post(self.user_url)
        assert response.status_code == 204
        # Token exists
        user_tokens = Token.objects.filter(user=self.user, type=self.token_type)
        token = user_tokens[0]
        assert len(user_tokens) == 1
        assert token.can_be_used
        # Email sent
        subject = Profile.EmailTemplate.VERIFY_EMAIL.subject
        assert_user_email_was_sent(self.user, subject)
