"""Tests for the 'Profile' model"""

# Personal
from jklib.django.db.tests import ModelTestCase

# Local
from ...models import Profile


# --------------------------------------------------------------------------------
# > TestCase
# --------------------------------------------------------------------------------
class TestProfile(ModelTestCase):
    """Tests our Profile model which extends the django User model"""

    model_class = Profile
    required_fields = ["user"]

    # ----------------------------------------
    # Behavior
    # ----------------------------------------
    @classmethod
    def setUpClass(cls):
        """Not implemented"""
        pass

    def setUp(self):
        """Creates a user and an admin user"""
        self.create_user()
        self.create_admin_user()

    def tearDown(self):
        """Not implemented"""
        pass

    @classmethod
    def tearDownClass(cls):
        """Not implemented"""
        pass

    # ----------------------------------------
    # Tests
    # ----------------------------------------
    def test_required_fields(self):
        """WIP"""
        pass

    def test_user_cascade_deletion(self):
        """WIP"""
        pass

    def test_send_password_updated_email(self):
        """WIP"""
        pass

    def test_send_reset_password_email(self):
        """WIP"""
        pass

    def test_send_verification_email(self):
        """WIP"""
        pass

    def test_send_welcome_email(self):
        """WIP"""
        pass
