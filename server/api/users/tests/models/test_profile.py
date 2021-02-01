"""Tests for the 'Profile' model"""

# Django
from django.db import transaction

# Personal
from jklib.django.db.tests import ModelTestCase

# Local
from ...models import Profile, Token
from ..utils import assert_user_email_was_sent


# --------------------------------------------------------------------------------
# > TestCase
# --------------------------------------------------------------------------------
class TestProfile(ModelTestCase):
    """
    Tests our Profile model which extends the django User model
    Split into the following sections:
        Behavior
        Field tests
        API tests
        Helpers
    """

    model_class = Profile

    # ----------------------------------------
    # Field tests
    # ----------------------------------------
    def test_required_fields(self):
        """Tests that you cannot create a Profile without a User"""
        with transaction.atomic():
            with self.assertRaises(self.common_errors):
                self.model_class.objects.create(is_verified=False)
        self.assert_instance_count_equals(0)

    def test_user(self):
        """Tests that 'user' cannot accept anything other than a User instance"""
        with transaction.atomic():
            # No user at all
            with self.assertRaises(self.common_errors):
                self.model_class.objects.create(is_verified=False)
            # Invalid user
            user = self.create_user()
            with self.assertRaises(self.common_errors):
                user.profile.user = "Not a user instance"
                user.profile.save()

    def test_is_verified(self):
        """Tests that 'is_verified' needs a boolean"""
        user = self.create_user()
        with self.assertRaises(self.common_errors):
            user.profile.is_verified = "Not boolean"
            user.profile.save()

    # ----------------------------------------
    # API tests
    # ----------------------------------------
    def test_user_cascade_deletion(self):
        """Tests that deleting a user also removes his Profile instance"""
        user_1 = self.create_user()
        self.create_user()
        self.assert_instance_count_equals(2)
        user_1.delete()
        self.assert_instance_count_equals(1)

    def test_send_password_updated_email(self):
        """Tests that the password updated email is sent correctly"""
        subject = self.model_class.EmailTemplate.PASSWORD_UPDATED.subject
        user = self.create_user()
        user.profile.send_password_updated_email()
        assert_user_email_was_sent(user, subject)

    def test_send_reset_password_email(self):
        """Tests that the reset password email is sent correctly with a valid token"""
        subject = self.model_class.EmailTemplate.REQUEST_PASSWORD_RESET.subject
        user = self.create_user()
        user.profile.send_reset_password_email()
        token_type, _ = Profile.RESET_TOKEN
        self._assert_token_has_been_created(user, token_type)
        assert_user_email_was_sent(user, subject)

    def test_send_verification_email(self):
        """Tests that the verification email is sent only to unverified users, and includes a valid token"""
        subject = self.model_class.EmailTemplate.VERIFY_EMAIL.subject
        user = self.create_user()
        # Verified
        user.profile.is_verified = True
        user.profile.save()
        user.profile.send_verification_email()
        with self.assertRaises((AssertionError, IndexError)):
            assert_user_email_was_sent(user, subject)
        # Not verified
        user.profile.is_verified = False
        user.profile.save()
        user.profile.send_verification_email()
        token_type, _ = Profile.VERIFY_TOKEN
        self._assert_token_has_been_created(user, token_type)
        assert_user_email_was_sent(user, subject)

    def test_send_welcome_email(self):
        """Tests that the welcome email is sent correctly"""
        subject = self.model_class.EmailTemplate.WELCOME.subject
        user = self.create_user()
        user.profile.send_welcome_email()
        assert_user_email_was_sent(user, subject)

    # ----------------------------------------
    # Helpers
    # ----------------------------------------
    @staticmethod
    def _assert_token_has_been_created(user, token_type):
        """
        Tests that there is ONE token in the database, and it matches with the user and type provided
        :param User user: The User instance we sent an email to
        :param str token_type: Type of the token, which depends on the email sent
        """
        token = Token.objects.get(user=user, type=token_type)
        assert Token.objects.count() == 1
        assert token.is_active_token
        assert token.can_be_used
