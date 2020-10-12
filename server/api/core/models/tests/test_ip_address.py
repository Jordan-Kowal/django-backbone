"""Tests for the 'IpAddress' model"""


# Built-in
from datetime import date

# Django
from django.db import IntegrityError

# Personal
from jklib.django.db.tests import ModelTestCase

# Local
from ...models import IpAddress


# --------------------------------------------------------------------------------
# > TestCase
# --------------------------------------------------------------------------------
class TestIpAddress(ModelTestCase):
    """TestCase for the 'IpAddress' model"""

    model_class = IpAddress
    required_fields = ["ip"]

    # ----------------------------------------
    # Behavior
    # ----------------------------------------
    @classmethod
    def setUpClass(cls):
        """WIP"""
        pass

    def setUp(self):
        """Creates a valid payload for an IpAddress"""
        self.payload = {
            "ip": "127.0.0.1",
            "status": IpAddress.IpStatus.NONE,
            "expires_on": date.today(),
            "active": False,
            "comment": "Created on setUp",
        }

    def tearDown(self):
        """Not implemented"""
        pass

    @classmethod
    def tearDownClass(cls):
        """Not implemented"""
        pass

    # ----------------------------------------
    # Field tests
    # ----------------------------------------
    def test_required_fields(self):
        """WIP"""
        self.assert_fields_are_required(self.payload)
        self.assert_instance_count_equals(0)

    def test_status_values(self):
        """WIP"""
        self.payload["status"] = "Invalid status"
        with self.assertRaises(ValueError):
            self.model_class(**self.payload).save()
        self.assert_instance_count_equals(0)

    def test_comment_length(self):
        """WIP"""
        self.payload["comment"] = "*" * 300
        with self.assertRaises((IntegrityError, ValueError)):
            self.model_class(**self.payload).save()
        self.assert_instance_count_equals(0)

    def test_successful_creation(self):
        """WIP"""
        self.model_class(**self.payload).save()
        self.assert_instance_count_equals(1)

    # ----------------------------------------
    # API tests
    # ----------------------------------------
    def test_blacklist(self):
        """WIP"""
        pass

    def test_clear(self):
        """WIP"""
        pass

    def test_is_blacklisted(self):
        """WIP"""
        pass

    def test_is_whitelisted(self):
        """WIP"""
        pass

    def test_whitelist(self):
        """WIP"""
        pass

    # ----------------------------------------
    # Cron tests
    # ----------------------------------------
    def test_clear_expired_entries(self):
        """WIP"""
        pass
