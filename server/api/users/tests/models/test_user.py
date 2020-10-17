"""Tests for the 'User' model"""

# Built-in
from random import randint, seed

# Django
from django.contrib.auth.models import User
from django.db import IntegrityError

# Personal
from jklib.django.db.tests import ModelTestCase

# Local
from ...models import Profile


# --------------------------------------------------------------------------------
# > TestCase
# --------------------------------------------------------------------------------
class TestUser(ModelTestCase):
    """Tests our customizations of the django User model"""

    model_class = User

    # ----------------------------------------
    # Behavior
    # ----------------------------------------
    @classmethod
    def setUpClass(cls):
        """Not implemented"""
        pass

    def setUp(self):
        """Generates random data that can be used to create a User"""
        self.payload = self.generate_random_user_data()

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
    def test_email_is_required(self):
        """(Signal) Tests that the email field is now required"""
        del self.payload["email"]
        with self.assertRaises(IntegrityError):
            self.model_class.objects.create(**self.payload)

    def test_email_is_unique(self):
        """Tests that the email field is now unique"""
        new_payload = self.generate_random_user_data()
        new_payload["email"] = self.payload["email"]
        self.model_class.objects.create(**self.payload)
        with self.assertRaises(IntegrityError):
            self.model_class.objects.create(**new_payload)

    def test_signal_username_is_email(self):
        """(Signal) Tests that the email automatically overrides the username on save"""
        # On create
        assert self.payload["username"] != self.payload["email"]
        user = self.model_class.objects.create_user(**self.payload)
        assert user.email == user.username
        # On update
        user.username = "New value"
        assert user.username != user.email
        user.save()
        assert user.username == user.email

    def test_signal_profile_is_created(self):
        """(Signal) Tests that a Profile instance is created whenever a User instance is created"""
        seed()
        n = randint(1, 10)
        for i in range(1, n):
            user = self.create_user()
            assert Profile.objects.filter(user=user).count() == 1
            assert Profile.objects.count() == i
