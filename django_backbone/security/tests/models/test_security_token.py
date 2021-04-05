"""Tests for the 'Token' model"""

# Built-in
from datetime import timedelta
from secrets import token_urlsafe

# Django
from django.utils import timezone

# Personal
from jklib.django.db.tests import ModelTestCase

# Local
from ...models import SecurityToken


# --------------------------------------------------------------------------------
# > TestCase
# --------------------------------------------------------------------------------
class TestToken(ModelTestCase):
    """Tests the Token model"""

    model_class = SecurityToken
    required_fields = ["user", "type", "value", "expired_at"]

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

    # ----------------------------------------
    # Properties Tests
    # ----------------------------------------
    def test_can_be_used(self):
        """Tests the 'can_be_used' property"""
        token = self.model_class.objects.create(**self.payload)
        assert token.can_be_used
        token.is_active_token = False
        assert not token.can_be_used
        token.is_active_token = True
        token.used_at = timezone.now()
        assert not token.can_be_used
        token.used_at = None
        token.expired_at = timezone.now()
        assert not token.can_be_used
        token.expired_at = timezone.now() + timedelta(days=1)
        assert token.can_be_used

    def test_is_expired(self):
        """Tests the 'is_expired' property"""
        token = self.model_class.objects.create(**self.payload)
        assert not token.is_expired
        token.expired_at = timezone.now() - timedelta(days=1)
        assert token.is_expired

    def test_is_used(self):
        """Tests the 'is_used' property"""
        token = self.model_class.objects.create(**self.payload)
        assert not token.is_used
        token.used_at = timezone.now() - timedelta(days=1)
        assert token.is_used

    # ----------------------------------------
    # API Tests
    # ----------------------------------------
    def test_consume_token(self):
        """Tests the API for consuming (and updating) a token"""
        token = self.model_class.create_new_token(self.user, "test", 600)
        assert token.used_at is None
        assert token.is_active_token
        token.consume_token()
        assert token.used_at is not None
        assert not token.is_active_token

    def test_create_new_token(self):
        """Tests the API for creating new token and deactivating previous ones"""
        self.model_class.create_new_token(self.user, "test", 600)
        self.assert_instance_count_equals(1)
        # Create token of same type, which should deactivate the first
        token_2 = self.model_class.create_new_token(self.user, "test", 600)
        token_1 = self.model_class.objects.get(pk=1)  # Refresh
        assert not token_1.can_be_used
        assert token_2.can_be_used
        # Create token of different type, not deactivating the second
        token_3 = self.model_class.create_new_token(self.user, "other", 600)
        token_2 = self.model_class.objects.get(pk=2)  # Refresh
        assert token_2.can_be_used
        assert token_3.can_be_used
        # Create token for a different user, does not impact the other users' tokens
        new_user = self.create_user()
        token_4 = self.model_class.create_new_token(new_user, "other", 600)
        token_3 = self.model_class.objects.get(pk=3)  # Refresh
        assert token_3.can_be_used
        assert token_4.can_be_used

    def test_deactivate_token(self):
        """Tests that deactivating a token makes it unusable"""
        token = self.model_class.objects.create(**self.payload)
        assert token.can_be_used
        token.deactivate_token()
        assert not token.can_be_used

    def test_deactivate_user_tokens(self):
        """Tests we can deactivate all tokens of a user"""
        shared_type = "type 3"
        other_user = self.create_user()
        self.model_class.create_new_token(self.user, "type 1", 600)
        self.model_class.create_new_token(self.user, "type 2", 600)
        self.model_class.create_new_token(self.user, shared_type, 600)
        self.model_class.create_new_token(other_user, shared_type, 600)
        self.assert_instance_count_equals(4)
        # Deactivate only type 1 for user 1
        self.model_class.deactivate_user_tokens(self.user, shared_type)
        tokens = SecurityToken.objects.all()
        usable_count, not_usable_count = 0, 0
        for token in tokens:
            if token.type == shared_type and token.user == self.user:
                assert not token.can_be_used
                not_usable_count += 1
            else:
                assert token.can_be_used
                usable_count += 1
        assert usable_count == 3
        assert not_usable_count == 1
        # Deactivate all tokens for user 1
        self.model_class.deactivate_user_tokens(self.user)
        tokens = SecurityToken.objects.all()
        usable_count, not_usable_count = 0, 0
        for token in tokens:
            if token.user == self.user:
                assert not token.can_be_used
                not_usable_count += 1
            else:
                assert token.can_be_used
                usable_count += 1
        assert usable_count == 1
        assert not_usable_count == 3

    def test_fetch_token_instance(self):
        """Tests we can fetch a valid and usable token instance"""
        token_type = "test"
        token = self.model_class.create_new_token(self.user, token_type, 600)
        self.assert_instance_count_equals(1)
        # Trying to fetch the instance
        assert (
            self.model_class.fetch_token_instance(token.value, token_type) is not None
        )
        assert self.model_class.fetch_token_instance("unknown", token_type) is None
        assert self.model_class.fetch_token_instance(token.value, "unknown") is None
        # Fetching a token that cannot be used
        token.is_active_token = False
        token.save()
        assert not token.can_be_used
        assert self.model_class.fetch_token_instance(token.value, token_type) is None

    # ----------------------------------------
    # Cron Jobs Tests
    # ----------------------------------------
    def test_cleanup_expired_unused_tokens(self):
        """Tests the clean up of expired and unused tokens"""
        # Creating 3 tokens
        self.model_class.create_new_token(self.user, "type 1", 600)
        token_2 = self.model_class.create_new_token(self.user, "type 2", 600)
        token_3 = self.model_class.create_new_token(self.user, "type 3", 600)
        # Changing some dates for eligibility
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
