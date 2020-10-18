"""Tests for the 'Token' model"""

# Built-in
from datetime import timedelta
from secrets import token_urlsafe

# Django
from django.db import IntegrityError, transaction
from django.utils import timezone

# Personal
from jklib.django.db.tests import ModelTestCase

# Local
from ...models import Token


# --------------------------------------------------------------------------------
# > TestCase
# --------------------------------------------------------------------------------
class TestToken(ModelTestCase):
    """Tests the Token model"""

    model_class = Token
    required_fields = ["user", "type", "value", "expired_at"]

    # ----------------------------------------
    # Behavior
    # ----------------------------------------
    @classmethod
    def setUpClass(cls):
        """Not implemented"""
        pass

    def setUp(self):
        """Creates a user and a payload that can be used for creating a token"""
        self.user = self.create_user()
        expiration_date = timezone.now() + timedelta(days=1)
        self.payload = {
            "user": self.user,
            "type": "random",
            "value": token_urlsafe(50),
            "expired_at": expiration_date,
            "used_at": None,
            "is_active_token": True,
        }

    def tearDown(self):
        """Not implemented"""
        pass

    @classmethod
    def tearDownClass(cls):
        """Not implemented"""
        pass

    # ----------------------------------------
    # Fields Tests
    # ----------------------------------------
    def test_required_fields(self):
        """Tests that the required fields are truly required"""
        self.assert_fields_are_required(self.payload)
        self.assert_instance_count_equals(0)

    def test_type_max_length(self):
        """Tests that the 'type' field max length is enforced"""
        self.payload["type"] = "a" * (self.model_class.TYPE_MAX_LENGTH + 1)
        with transaction.atomic():
            with self.assertRaises((IntegrityError, ValueError)):
                self.model_class.objects.create(**self.payload)
        self.assert_instance_count_equals(0)

    def test_unique_value(self):
        """Tests the unique constraint of the 'value' field"""
        token = self.model_class.objects.create(**self.payload)
        user_2 = self.create_user()
        expiration_date_2 = timezone.now() + timedelta(days=2)
        payload_2 = self.payload = {
            "user": user_2,
            "type": "random_2",
            "value": token.value,
            "expired_at": expiration_date_2,
            "used_at": None,
            "is_active_token": True,
        }
        # Creating the second token should not work
        with transaction.atomic():
            with self.assertRaises(IntegrityError):
                self.model_class.objects.create(**payload_2)
        self.assert_instance_count_equals(1)

    # ----------------------------------------
    # Properties Tests
    # ----------------------------------------
    def test_can_be_used(self):
        """Tests he 'can_be_used' property"""
        # Initial token can be used
        token = self.model_class.objects.create(**self.payload)
        assert token.can_be_used
        # Changing is_active_token
        token.is_active_token = False
        assert not token.can_be_used
        token.is_active_token = True
        assert token.can_be_used
        # Changing used_at
        token.used_at = timezone.now()
        assert not token.can_be_used
        token.used_at = None
        assert token.can_be_used
        # Changing expired_at
        token.expired_at = timezone.now()
        assert not token.can_be_used
        token.expired_at = timezone.now() + timedelta(days=1)
        assert token.can_be_used

    def test_is_expired(self):
        """Tests he 'is_expired' property"""
        token = self.model_class.objects.create(**self.payload)
        assert not token.is_expired
        token.expired_at = timezone.now() - timedelta(days=1)
        assert token.is_expired

    def test_is_used(self):
        """Tests he 'is_used' property"""
        token = self.model_class.objects.create(**self.payload)
        assert not token.is_used
        token.used_at = timezone.now() - timedelta(days=1)
        assert token.is_used

    # ----------------------------------------
    # API Tests
    # ----------------------------------------
    def test_consume_token(self):
        """Tests the API for consuming (and updating) a token"""
        token, value = self.model_class.create_new_token(self.user, "test", 600)
        assert token.used_at is None
        assert token.is_active_token
        token.consume_token()
        assert token.used_at is not None
        assert not token.is_active_token

    def test_create_new_token(self):
        """Tests the API for creating new token and deprecating previous ones"""
        # Create one token
        token_instance_1, token_value_1 = self.model_class.create_new_token(
            self.user, "test", 600
        )
        self.assert_instance_count_equals(1)
        token_1 = self.model_class.objects.get(pk=1)
        assert token_1 == token_instance_1
        assert token_1.value == token_value_1
        # Create token of same type, deactivating the first
        self.model_class.create_new_token(self.user, "test", 600)
        token_1 = self.model_class.objects.get(pk=1)  # Refresh
        token_2 = self.model_class.objects.get(pk=2)
        assert not token_1.can_be_used
        assert token_2.can_be_used
        # Create token of different type, not deactivating the second
        self.model_class.create_new_token(self.user, "other", 600)
        token_3 = self.model_class.objects.get(pk=2)
        assert token_2.can_be_used
        assert token_3.can_be_used
        # Create token for a different user, does not impact the other users' tokens
        new_user = self.create_user()
        self.model_class.create_new_token(new_user, "other", 600)
        token_4 = self.model_class.objects.get(pk=4)
        assert token_3.can_be_used
        assert token_4.can_be_used

    def test_deactivate_token(self):
        """Tests that deactivating a token makes it unusable"""
        token = self.model_class.objects.create(**self.payload)
        assert token.can_be_used
        token.deactivate_token()
        assert not token.can_be_used

    def test_deactivate_user_tokens(self):
        """Tests the API for deactivating tokens for a user"""
        # Create 5 tokens for our user
        for i in range(1, 6):
            self.model_class.create_new_token(self.user, f"type {i}", 600)
        self.assert_instance_count_equals(5)
        # Create 1 token of similar type, for another user
        shared_type = "type 1"
        user_2 = self.create_user()
        self.model_class.create_new_token(user_2, shared_type, 600)
        self.assert_instance_count_equals(6)
        # Deactivate only type 1 for user 1
        self.model_class.deactivate_user_tokens(self.user, shared_type)
        tokens = Token.objects.all()
        for token in tokens:
            if token.type == shared_type and token.user == self.user:
                assert not token.can_be_used
            else:
                assert token.can_be_used
        # Deactivate all user 1 tokens
        self.model_class.deactivate_user_tokens(self.user)
        tokens = Token.objects.all()
        for token in tokens:
            if token.user == self.user:
                assert not token.can_be_used
            else:
                assert token.can_be_used

    def test_fetch_token_instance(self):
        """Tests the API for fetching a valid and usable token instance"""
        token_type = "test"
        token, value = self.model_class.create_new_token(self.user, token_type, 600)
        self.assert_instance_count_equals(1)
        # Fetching the instance
        assert self.model_class.fetch_token_instance(value, token_type) is not None
        # Fetching an instance using invalid values
        assert self.model_class.fetch_token_instance("unknown", token_type) is None
        assert self.model_class.fetch_token_instance(value, "unknown") is None
        # Fetching a token that cannot be used
        token.is_active_token = False
        token.save()
        assert not token.can_be_used
        assert self.model_class.fetch_token_instance(value, token_type) is None

    # ----------------------------------------
    # Cron Jobs Tests
    # ----------------------------------------
    def test_cleanup_expired_unused_tokens(self):
        """Tests the job in charge of removing unused expired entries"""
        # Creating 3 tokens
        token_1, _ = self.model_class.create_new_token(self.user, "type 1", 600)
        token_2, _ = self.model_class.create_new_token(self.user, "type 2", 600)
        token_3, _ = self.model_class.create_new_token(self.user, "type 3", 600)
        # Changing some dates for eligiblity
        previous_date = timezone.now() - timedelta(days=1)
        token_2.expired_at = previous_date
        token_2.save()
        token_3.expired_at = previous_date
        token_3.used_at = previous_date
        token_3.save()
        # Only token 2 should get removed
        self.model_class.cleanup_expired_unused_tokens()
        self.assert_instance_count_equals(2)
        with self.assertRaises(self.model_class.DoesNotExist):
            self.model_class.objects.get(pk=2)
