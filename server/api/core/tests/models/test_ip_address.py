"""Tests for the 'IpAddress' model"""


# Built-in
from datetime import date, timedelta

# Django
from django.conf import settings
from django.db import IntegrityError

# Personal
from jklib.django.db.tests import ModelTestCase
from jklib.django.utils.network import get_client_ip

# Local
from ...models import IpAddress


# --------------------------------------------------------------------------------
# > TestCase
# --------------------------------------------------------------------------------
class TestIpAddress(ModelTestCase):
    """
    TestCase for the 'IpAddress' model
    Split into the following sections:
        Behavior
        Field tests
        Instance properties tests
        Instance API tests
        Request API tests
        Cron tests
        Helpers
    """

    model_class = IpAddress
    required_fields = ["ip", "status"]

    # ----------------------------------------
    # Behavior
    # ----------------------------------------
    @classmethod
    def setUpClass(cls):
        """Not implemented"""
        pass

    def setUp(self):
        """Creates a valid payload for an IpAddress"""
        self.payload = {
            "ip": "127.0.0.1",
            "status": IpAddress.IpStatus.NONE,
            "expires_on": None,
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
        """Tests that the required fields are truly required"""
        self.assert_fields_are_required(self.payload)
        self.assert_instance_count_equals(0)

    def test_signal_status_choices(self):
        """(Signal) Tests that only a valid 'status' can be provided"""
        self.payload["status"] = "Invalid status"
        with self.assertRaises(ValueError):
            self.model_class(**self.payload).save()
        self.assert_instance_count_equals(0)

    def test_signal_comment_length(self):
        """(Signal) Tests that the comment max_length cannot be exceeded"""
        self.payload["comment"] = "a" * (self.model_class.COMMENT_MAX_LENGTH + 1)
        with self.assertRaises((IntegrityError, ValueError)):
            self.model_class(**self.payload).save()
        self.assert_instance_count_equals(0)

    def test_successful_creation(self):
        """Tests that the model can be created successfully"""
        self.model_class(**self.payload).save()
        self.assert_instance_count_equals(1)

    # ----------------------------------------
    # Instance properties tests
    # ----------------------------------------
    def test_is_blacklisted(self):
        """Tests that a blacklisted IP is flagged as blacklisted"""
        instance = self.model_class.objects.create(**self.payload)
        instance.blacklist()
        assert instance.is_blacklisted

    def test_is_whitelisted(self):
        """Tests that a whitelisted IP is flagged as whitelisted"""
        instance = self.model_class.objects.create(**self.payload)
        instance.whitelist()
        assert instance.is_whitelisted

    # ----------------------------------------
    # Instance API tests
    # ----------------------------------------
    def test_blacklist_general_behavior(self):
        """Tests the general behavior of the blacklist method"""
        instance = self.model_class.objects.create(**self.payload)
        new_comment = "Blacklisted"
        end_date = date.today() + timedelta(days=3)
        instance.blacklist(end_date=end_date, comment=new_comment)
        assert instance.status == IpAddress.IpStatus.BLACKLISTED
        assert instance.active
        assert instance.expires_on == end_date
        assert instance.comment == new_comment

    def test_blacklist_without_end_date(self):
        """Tests that the end_date is defaulted if not provided when blacklisting"""
        instance = self.model_class.objects.create(**self.payload)
        instance.blacklist()
        default_end_date = date.today() + timedelta(
            days=settings.IP_STATUS_DEFAULT_DURATION
        )
        assert instance.active
        assert instance.status == IpAddress.IpStatus.BLACKLISTED
        assert instance.expires_on == default_end_date

    def test_blacklist_override(self):
        """Tests that a whitelisted IP can be blacklisted only with the 'override' argument"""
        end_date = date.today() + timedelta(days=3)
        self.payload["status"] = IpAddress.IpStatus.WHITELISTED
        instance = self.model_class.objects.create(**self.payload)
        # Without override
        instance.blacklist(override=False, end_date=end_date)
        assert not instance.active
        assert instance.status == IpAddress.IpStatus.WHITELISTED
        assert instance.expires_on == self.payload["expires_on"] != end_date
        # With override
        instance.blacklist(override=True, end_date=end_date)
        assert instance.active
        assert instance.status == IpAddress.IpStatus.BLACKLISTED
        assert instance.expires_on == end_date

    def test_clear(self):
        """Tests 'clear' correctly resets the model fields"""
        self.payload["active"] = True
        self.payload["status"] = IpAddress.IpStatus.BLACKLISTED
        self.payload["expires_on"] = date.today()
        instance = self.model_class.objects.create(**self.payload)
        instance.clear()
        assert not instance.active
        assert instance.status == IpAddress.IpStatus.NONE
        assert instance.expires_on is None

    def test_whitelist_general_behavior(self):
        """Tests the general behavior of the whitelist method"""
        instance = self.model_class.objects.create(**self.payload)
        new_comment = "Whitelisted"
        end_date = date.today() + timedelta(days=3)
        instance.whitelist(end_date=end_date, comment=new_comment)
        assert instance.status == IpAddress.IpStatus.WHITELISTED
        assert instance.active
        assert instance.expires_on == end_date
        assert instance.comment == new_comment

    def test_whitelist_without_end_date(self):
        """Tests that the end_date is defaulted if not provided when whitelisting"""
        instance = self.model_class.objects.create(**self.payload)
        instance.whitelist()
        default_end_date = date.today() + timedelta(
            days=settings.IP_STATUS_DEFAULT_DURATION
        )
        assert instance.active
        assert instance.status == IpAddress.IpStatus.WHITELISTED
        assert instance.expires_on == default_end_date

    def test_whitelist_override(self):
        """Tests that a blacklisted IP can be whilisted only with the 'override' argument"""
        end_date = date.today() + timedelta(days=3)
        self.payload["status"] = IpAddress.IpStatus.BLACKLISTED
        instance = self.model_class.objects.create(**self.payload)
        # Without override
        instance.whitelist(override=False, end_date=end_date)
        assert not instance.active
        assert instance.status == IpAddress.IpStatus.BLACKLISTED
        assert instance.expires_on == self.payload["expires_on"] != end_date
        # With override
        instance.whitelist(override=True, end_date=end_date)
        assert instance.active
        assert instance.status == IpAddress.IpStatus.WHITELISTED
        assert instance.expires_on == end_date

    # ----------------------------------------
    # Request API tests
    # ----------------------------------------
    def test_blacklist_from_request_general_behavior(self):
        """Tests the general behavior of the blacklist_from_request method"""
        fake_request = self.build_fake_request()
        new_comment = "Blacklisted"
        end_date = date.today() + timedelta(days=3)
        instance = self.model_class.blacklist_from_request(
            fake_request, end_date=end_date, comment=new_comment
        )
        assert instance.status == IpAddress.IpStatus.BLACKLISTED
        assert instance.active
        assert instance.expires_on == end_date
        assert instance.comment == new_comment

    def test_blacklist_from_request_without_end_date(self):
        """Tests that the end_date is defaulted if not provided when blacklisting from request"""
        fake_request = self.build_fake_request()
        instance = self.model_class.blacklist_from_request(fake_request)
        default_end_date = date.today() + timedelta(
            days=settings.IP_STATUS_DEFAULT_DURATION
        )
        assert instance.active
        assert instance.status == IpAddress.IpStatus.BLACKLISTED
        assert instance.expires_on == default_end_date

    def test_blacklist_from_request_override(self):
        """Tests that a whitelisted IP can be blacklisted only with the 'override' argument"""
        fake_request = self.build_fake_request()
        fake_ip_address = get_client_ip(fake_request)
        self.payload["ip"] = fake_ip_address
        self.payload["status"] = IpAddress.IpStatus.WHITELISTED
        self.model_class.objects.create(**self.payload)
        end_date = date.today() + timedelta(days=3)
        # Without override
        instance = self.model_class.blacklist_from_request(
            fake_request, end_date=end_date, override=False
        )
        assert not instance.active
        assert instance.status == IpAddress.IpStatus.WHITELISTED
        assert instance.expires_on == self.payload["expires_on"] != end_date
        # With override
        instance = self.model_class.blacklist_from_request(
            fake_request, end_date=end_date, override=True
        )
        assert instance.active
        assert instance.status == IpAddress.IpStatus.BLACKLISTED
        assert instance.expires_on == end_date

    def test_clear_from_request(self):
        """Tests 'clear_from_request' correctly resets the model fields"""
        fake_request = self.build_fake_request()
        fake_ip_address = get_client_ip(fake_request)
        self.payload["ip"] = fake_ip_address
        self.payload["active"] = True
        self.payload["status"] = IpAddress.IpStatus.BLACKLISTED
        self.payload["expires_on"] = date.today()
        self.model_class.objects.create(**self.payload)
        instance = self.model_class.clear_from_request(fake_request)
        assert not instance.active
        assert instance.status == IpAddress.IpStatus.NONE
        assert instance.expires_on is None

    def test_whitelist_from_request_general_behavior(self):
        """Tests the general behavior of the whitelist_from_request method"""
        fake_request = self.build_fake_request()
        new_comment = "Whitelisted"
        end_date = date.today() + timedelta(days=3)
        instance = self.model_class.whitelist_from_request(
            fake_request, end_date=end_date, comment=new_comment
        )
        assert instance.status == IpAddress.IpStatus.WHITELISTED
        assert instance.active
        assert instance.expires_on == end_date
        assert instance.comment == new_comment

    def test_whitelist_from_request_without_end_date(self):
        """Tests that the end_date is defaulted if not provided when whitelisting from request"""
        fake_request = self.build_fake_request()
        instance = self.model_class.whitelist_from_request(fake_request)
        default_end_date = date.today() + timedelta(
            days=settings.IP_STATUS_DEFAULT_DURATION
        )
        assert instance.active
        assert instance.status == IpAddress.IpStatus.WHITELISTED
        assert instance.expires_on == default_end_date

    def test_whitelist_from_request_override(self):
        """Tests that a blacklisted IP can be whitelisted only with the 'override' argument"""
        fake_request = self.build_fake_request()
        fake_ip_address = get_client_ip(fake_request)
        self.payload["ip"] = fake_ip_address
        self.payload["status"] = IpAddress.IpStatus.BLACKLISTED
        self.model_class.objects.create(**self.payload)
        end_date = date.today() + timedelta(days=3)
        # Without override
        instance = self.model_class.whitelist_from_request(
            fake_request, end_date=end_date, override=False
        )
        assert not instance.active
        assert instance.status == IpAddress.IpStatus.BLACKLISTED
        assert instance.expires_on == self.payload["expires_on"] != end_date
        # With override
        instance = self.model_class.whitelist_from_request(
            fake_request, end_date=end_date, override=True
        )
        assert instance.active
        assert instance.status == IpAddress.IpStatus.WHITELISTED
        assert instance.expires_on == end_date

    def test_is_blacklisted_from_request(self):
        """Tests that a blacklisted IP is flagged as blacklisted"""
        fake_request = self.build_fake_request()
        fake_ip_address = get_client_ip(fake_request)
        self.payload["ip"] = fake_ip_address
        self.model_class.objects.create(**self.payload)
        self.model_class.blacklist_from_request(fake_request)
        assert self.model_class.is_blacklisted_from_request(fake_request)

    def test_is_whitelisted_from_request(self):
        """Tests that a whitelisted IP is flagged as whitelisted"""
        fake_request = self.build_fake_request()
        fake_ip_address = get_client_ip(fake_request)
        self.payload["ip"] = fake_ip_address
        self.model_class.objects.create(**self.payload)
        self.model_class.whitelist_from_request(fake_request)
        assert self.model_class.is_whitelisted_from_request(fake_request)

    # ----------------------------------------
    # Cron tests
    # ----------------------------------------
    def test_clear_expired_entries(self):
        """Tests that only the eligible entries are correctly cleared"""
        payloads, instances, clear_eligibility = self._create_ips_for_clear_test()
        IpAddress.clear_expired_entries()
        for payload, instance, cleared in zip(payloads, instances, clear_eligibility):
            if cleared:
                updated_instance = self.model_class.objects.get(pk=instance.id)
                assert updated_instance.expires_on is None
                assert not updated_instance.active
                assert updated_instance.status == IpAddress.IpStatus.NONE
            else:
                assert instance.expires_on == payload["expires_on"]
                assert instance.active == payload["active"]
                assert instance.status == payload["status"]

    # ----------------------------------------
    # Helpers
    # ----------------------------------------
    def _create_ips_for_clear_test(self):
        """
        Builds various IPs allowing us to test various scenarios for the clearing cron job
        Returns 3 lists:
            The payload used for the instances
            The instances themselves
            Whether they will be cleared
        :return: 3 lists of identical sizes
        :rtype: tuple(list, list, list)
        """
        # Prepare data
        expired_date = date.today() - timedelta(days=5)
        valid_date = date.today() + timedelta(days=3)
        data = [
            # IP, Status, Expires on, Active, Whether it should be cleared
            ("127.0.0.1", IpAddress.IpStatus.NONE, None, False, False),
            ("127.0.0.2", IpAddress.IpStatus.BLACKLISTED, expired_date, True, True),
            ("127.0.0.3", IpAddress.IpStatus.WHITELISTED, None, False, False),
            ("127.0.0.4", IpAddress.IpStatus.BLACKLISTED, valid_date, True, False),
            ("127.0.0.5", IpAddress.IpStatus.WHITELISTED, expired_date, True, True),
        ]
        instances = []
        clear_eligibility = []
        payloads = []
        # Create instances and store data in lists
        for row in data:
            payload = {
                "ip": row[0],
                "status": row[1],
                "expires_on": row[2],
                "active": row[3],
            }
            to_be_cleared = row[4]
            instance = self.model_class.objects.create(**payload)
            payloads.append(payload)
            instances.append(instance)
            clear_eligibility.append(to_be_cleared)
        return payloads, instances, clear_eligibility
