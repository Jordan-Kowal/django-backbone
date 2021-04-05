"""Tests for the 'users' app models"""


# Personal
from jklib.django.db.tests import ModelTestCase

# Application
from security.models import SecurityToken

# Local
from ..models import User, UserEmailTemplate

# --------------------------------------------------------------------------------
# > Utilities
# --------------------------------------------------------------------------------
FAKE_EMAIL = "fake_email@fake_domain.com"
FAKE_PASSWORD = "F4k3P4ssw0rD!"


# --------------------------------------------------------------------------------
# > TestCase
# --------------------------------------------------------------------------------
class TestUser(ModelTestCase):
    """TestCase for the 'User' model"""

    model_class = User

    def setUp(self):
        """Creates a user"""
        self.user = self.create_user()

    # ----------------------------------------
    # Properties tests
    # ----------------------------------------
    def test_full_name(self):
        """Tests the `full_name` property"""
        full_name = "Fake Username"
        first_name, last_name = full_name.split(" ")
        self.user.first_name = first_name
        self.user.last_name = last_name
        self.user.save()
        assert self.user.full_name == full_name

    # ----------------------------------------
    # Creation API tests
    # ----------------------------------------
    def test_create_user(self):
        """Tests we can create a user"""
        user = self.model_class.create_user(FAKE_EMAIL, FAKE_PASSWORD)
        assert not user.is_staff
        assert not user.is_superuser

    def test_create_admin(self):
        """Tests we can create an admin"""
        user = self.model_class.create_admin(FAKE_EMAIL, FAKE_PASSWORD)
        assert user.is_staff
        assert not user.is_superuser
        with self.assertRaises(ValueError):
            self.model_class.create_superuser(
                "fake_email_2@fake_domain.com", FAKE_PASSWORD, is_staff=False
            )

    def test_create_superuser(self):
        """Tests we can create a superuser"""
        user = self.model_class.create_superuser(FAKE_EMAIL, FAKE_PASSWORD)
        assert user.is_staff
        assert user.is_superuser
        with self.assertRaises(ValueError):
            self.model_class.create_superuser(
                "fake_email_2@fake_domain.com", FAKE_PASSWORD, is_staff=False
            )
        with self.assertRaises(ValueError):
            self.model_class.create_superuser(
                "fake_email_3@fake_domain.com", FAKE_PASSWORD, is_superuser=False
            )

    # ----------------------------------------
    # Email API tests
    # ----------------------------------------
    def test_send_password_updated_email(self):
        """Tests that the password updated email is sent correctly"""
        subject = UserEmailTemplate.PASSWORD_UPDATED.subject
        self.user.send_password_updated_email()
        self.assert_email_was_sent(subject, to=[self.user.email], async_=True)

    def test_send_reset_password_email(self):
        """Tests that the reset password email is sent correctly and includes a token"""
        subject = UserEmailTemplate.REQUEST_PASSWORD_RESET.subject
        token_type, token_duration = self.model_class.RESET_TOKEN
        token = SecurityToken.create_new_token(self.user, token_type, token_duration)
        async_ = False
        self.user.send_reset_password_email(token, async_)
        self.assert_email_was_sent(subject, to=[self.user.email], async_=async_)
        with self.assertRaises(ValueError):
            token.is_active_token = False
            token.save()
            self.user.send_reset_password_email(token, async_)
        with self.assertRaises(TypeError):
            token_2 = SecurityToken.create_new_token(
                self.user, "BadType", token_duration
            )
            self.user.send_reset_password_email(token_2, async_)

    def test_send_verification_email(self):
        """Tests that the verification email is sent (only to non-verified users) and includes a token"""
        subject = UserEmailTemplate.VERIFY_EMAIL.subject
        token_type, token_duration = self.model_class.VERIFY_TOKEN
        token = SecurityToken.create_new_token(self.user, token_type, token_duration)
        async_ = False
        # Verified
        self.user.is_verified = True
        self.user.save()
        self.user.send_verification_email(token, async_)
        with self.assertRaises((AssertionError, IndexError)):
            self.assert_email_was_sent(subject, to=[self.user.email], async_=async_)
        # Not verified
        self.user.is_verified = False
        self.user.save()
        self.user.send_verification_email(token, async_)
        self.assert_email_was_sent(subject, to=[self.user.email], async_=async_)
        with self.assertRaises(ValueError):
            token.is_active_token = False
            token.save()
            self.user.send_reset_password_email(token, async_)
        with self.assertRaises(TypeError):
            token_2 = SecurityToken.create_new_token(
                self.user, "BadType", token_duration
            )
            self.user.send_reset_password_email(token_2, async_)

    def test_send_welcome_email(self):
        """Tests that the welcome email is sent correctly"""
        subject = UserEmailTemplate.WELCOME.subject
        self.user.send_welcome_email()
        self.assert_email_was_sent(subject, to=[self.user.email], async_=True)
