"""TestCase for the 'send_verification_email' action"""

# Django
from django.contrib.auth.models import User
from django.core import mail
from rest_framework.test import APIClient

# Personal
from jklib.django.drf.tests import ActionTestCase

# Local
from ...models import Profile, Token
from ._shared import USER_SERVICE_URL


# --------------------------------------------------------------------------------
# > TestCase
# --------------------------------------------------------------------------------
class TestSendVerificationEmail(ActionTestCase):
    """TestCase for the 'update_password' action"""

    service_base_url = f"{USER_SERVICE_URL}/self/send_verification_email/"

    # ----------------------------------------
    # Behavior
    # ----------------------------------------
    @classmethod
    def setUpClass(cls):
        """Sets up the API client"""
        cls.client = APIClient()

    def setUp(self):
        """Creates 1 basic user"""
        self.user = self.create_user()

    def teardown(self):
        """Removes all users and tokens from the database and logs out the current client"""
        User.objects.all().delete()
        Token.objects.all().delete()
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
        response = self.client.post(self.service_base_url)
        assert response.status_code == 401
        # 204 Ok
        self.client.force_authenticate(self.user)
        response = self.client.post(self.service_base_url)
        assert response.status_code == 204
        # 403 Already verified
        self.user.profile.is_verified = True
        self.user.profile.save()
        response = self.client.post(self.service_base_url)
        assert response.status_code == 403

    def test_success(self):
        """Tests that the verification token is created and the email is sent"""
        self.client.force_authenticate(self.user)
        # Response 204
        response = self.client.post(self.service_base_url)
        assert response.status_code == 204
        # Token exists
        user_tokens = Token.objects.filter(user=self.user, type="verify")
        token = user_tokens[0]
        assert len(user_tokens) == 1
        assert token.can_be_used
        # Email sent
        subject = Profile.EMAILS["verify_email"]["subject"]
        self.assert_email_was_sent(subject, async_=False)
