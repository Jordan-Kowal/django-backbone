"""Tests for the 'NetworkRule' model"""


# Built-in
from datetime import date, timedelta

# Django
from django.conf import settings

# Personal
from jklib.django.db.tests import ModelTestCase
from jklib.django.utils.network import get_client_ip
from jklib.django.utils.tests import assert_logs

# Local
from ...models import NetworkRule


# --------------------------------------------------------------------------------
# > TestCase
# --------------------------------------------------------------------------------
class TestNetworkRule(ModelTestCase):
    """
    TestCase for the 'NetworkRule' model
    Split into the following sections:
        Behavior
        Field tests
        Instance properties tests
        Instance API tests
        Request API tests
        Cron tests
        Helpers
    """

    model_class = NetworkRule
    required_fields = ["ip", "status"]

    # ----------------------------------------
    # Behavior
    # ----------------------------------------
    def setUp(self):
        """Creates a valid payload for a NetworkRule"""
        self.payload = {
            "ip": "127.0.0.1",
            "status": NetworkRule.Status.NONE,
            "expires_on": None,
            "active": False,
            "comment": "Created on setUp",
        }

    # ----------------------------------------
    # Field tests
    # ----------------------------------------
    def test_required_fields(self):
        """Tests that the required fields are truly required"""
        self.assert_fields_are_required(self.payload)
        self.assert_instance_count_equals(0)

    def test_ip(self):
        """Tests that the ip address must be valid"""
        self.payload["ip"] = "Invalid IP"
        with self.assertRaises(self.common_errors):
            self.model_class(**self.payload).save()
        self.assert_instance_count_equals(0)

    def test_status(self):
        """Tests that only a valid 'status' can be provided"""
        self.payload["status"] = "Invalid status"
        with self.assertRaises(self.common_errors):
            self.model_class(**self.payload).save()
        self.assert_instance_count_equals(0)

    def test_expires_on(self):
        """Tests that the date must be valid"""
        self.payload["expires_on"] = "Invalid date"
        with self.assertRaises(self.common_errors):
            self.model_class(**self.payload).save()
        self.assert_instance_count_equals(0)

    def test_active(self):
        """Tests that the active field must be valid"""
        self.payload["active"] = "Not a boolean"
        with self.assertRaises(self.common_errors):
            self.model_class(**self.payload).save()
        self.assert_instance_count_equals(0)

    def test_comment(self):
        """Tests that the comment max_length cannot be exceeded"""
        self.payload["comment"] = "a" * (self.model_class.COMMENT_MAX_LENGTH + 1)
        with self.assertRaises(self.common_errors):
            self.model_class(**self.payload).save()
        self.assert_instance_count_equals(0)

    @assert_logs(logger="security", level="INFO")
    def test_successful_creation(self):
        """Tests that the model can be created successfully"""
        self.model_class.objects.create(**self.payload)
        self.assert_instance_count_equals(1)

    # ----------------------------------------
    # Instance properties tests
    # ----------------------------------------
    @assert_logs("security", "INFO")
    def test_get_default_duration(self):
        """Tests the default duration returns the settings duration"""
        instance = self.model_class.objects.create(**self.payload)
        if hasattr(settings, "NETWORK_RULE_DEFAULT_DURATION"):
            assert (
                instance.get_default_duration()
                == settings.NETWORK_RULE_DEFAULT_DURATION
            )
        else:
            assert instance.get_default_duration() == instance.DEFAULT_DURATION

    @assert_logs(logger="security", level="INFO")
    def test_computed_status(self):
        """Tests the computed_status works as intended"""
        instance = self.model_class.objects.create(**self.payload)
        instance.whitelist(override=True)
        assert instance.computed_status == "whitelisted"
        instance.blacklist(override=True)
        assert instance.computed_status == "blacklisted"
        instance.clear()
        assert instance.computed_status == "inactive"

    @assert_logs(logger="security", level="INFO")
    def test_is_blacklisted(self):
        """Tests that a blacklisted rule is correctly flagged as blacklisted"""
        instance = self.model_class.objects.create(**self.payload)
        instance.blacklist()
        assert instance.is_blacklisted
        instance.whitelist(override=True)
        assert not instance.is_blacklisted

    @assert_logs(logger="security", level="INFO")
    def test_is_whitelisted(self):
        """Tests that a whitelisted rule is correctly flagged as whitelisted"""
        instance = self.model_class.objects.create(**self.payload)
        instance.whitelist()
        assert instance.is_whitelisted
        instance.blacklist(override=True)
        assert not instance.is_whitelisted

    # ----------------------------------------
    # Instance API tests
    # ----------------------------------------
    @assert_logs(logger="security", level="INFO")
    def test_blacklist_general_behavior(self):
        """Tests the general behavior of the blacklist method"""
        instance = self.model_class.objects.create(**self.payload)
        new_comment = "Blacklisted"
        end_date = date.today() + timedelta(days=3)
        instance.blacklist(end_date=end_date, comment=new_comment)
        assert instance.status == NetworkRule.Status.BLACKLISTED
        assert instance.active
        assert instance.expires_on == end_date
        assert instance.comment == new_comment

    @assert_logs(logger="security", level="INFO")
    def test_blacklist_without_end_date(self):
        """Tests that the end_date is defaulted if not provided when blacklisting"""
        instance = self.model_class.objects.create(**self.payload)
        instance.blacklist()
        default_end_date = date.today() + timedelta(
            days=instance.get_default_duration()
        )
        assert instance.active
        assert instance.status == NetworkRule.Status.BLACKLISTED
        assert instance.expires_on == default_end_date

    @assert_logs(logger="security", level="INFO")
    def test_blacklist_override(self):
        """Tests that a whitelisted rule can be blacklisted only with the 'override' argument"""
        end_date = date.today() + timedelta(days=3)
        self.payload["status"] = NetworkRule.Status.WHITELISTED
        instance = self.model_class.objects.create(**self.payload)
        # Without override
        instance.blacklist(override=False, end_date=end_date)
        assert not instance.active
        assert instance.status == NetworkRule.Status.WHITELISTED
        assert instance.expires_on == self.payload["expires_on"] != end_date
        # With override
        instance.blacklist(override=True, end_date=end_date)
        assert instance.active
        assert instance.status == NetworkRule.Status.BLACKLISTED
        assert instance.expires_on == end_date

    @assert_logs(logger="security", level="INFO")
    def test_clear(self):
        """Tests 'clear' correctly resets the model fields"""
        self.payload["active"] = True
        self.payload["status"] = NetworkRule.Status.BLACKLISTED
        self.payload["expires_on"] = date.today()
        instance = self.model_class.objects.create(**self.payload)
        instance.clear()
        assert not instance.active
        assert instance.status == NetworkRule.Status.NONE
        assert instance.expires_on is None

    @assert_logs(logger="security", level="INFO")
    def test_whitelist_general_behavior(self):
        """Tests the general behavior of the whitelist method"""
        instance = self.model_class.objects.create(**self.payload)
        new_comment = "Whitelisted"
        end_date = date.today() + timedelta(days=3)
        instance.whitelist(end_date=end_date, comment=new_comment)
        assert instance.status == NetworkRule.Status.WHITELISTED
        assert instance.active
        assert instance.expires_on == end_date
        assert instance.comment == new_comment

    @assert_logs(logger="security", level="INFO")
    def test_whitelist_without_end_date(self):
        """Tests that the end_date is defaulted if not provided when whitelisting"""
        instance = self.model_class.objects.create(**self.payload)
        instance.whitelist()
        default_end_date = date.today() + timedelta(
            days=instance.get_default_duration()
        )
        assert instance.active
        assert instance.status == NetworkRule.Status.WHITELISTED
        assert instance.expires_on == default_end_date

    @assert_logs(logger="security", level="INFO")
    def test_whitelist_override(self):
        """Tests that a blacklisted rule can be whitelisted only with the 'override' argument"""
        end_date = date.today() + timedelta(days=3)
        self.payload["status"] = NetworkRule.Status.BLACKLISTED
        instance = self.model_class.objects.create(**self.payload)
        # Without override
        instance.whitelist(override=False, end_date=end_date)
        assert not instance.active
        assert instance.status == NetworkRule.Status.BLACKLISTED
        assert instance.expires_on == self.payload["expires_on"] != end_date
        # With override
        instance.whitelist(override=True, end_date=end_date)
        assert instance.active
        assert instance.status == NetworkRule.Status.WHITELISTED
        assert instance.expires_on == end_date

    # ----------------------------------------
    # Request API tests
    # ----------------------------------------
    @assert_logs(logger="security", level="INFO")
    def test_blacklist_from_request_general_behavior(self):
        """Tests the general behavior of the blacklist_from_request method"""
        fake_request = self.build_fake_request()
        new_comment = "Blacklisted"
        end_date = date.today() + timedelta(days=3)
        instance = self.model_class.blacklist_from_request(
            fake_request, end_date=end_date, comment=new_comment
        )
        assert instance.status == NetworkRule.Status.BLACKLISTED
        assert instance.active
        assert instance.expires_on == end_date
        assert instance.comment == new_comment

    @assert_logs(logger="security", level="INFO")
    def test_blacklist_from_request_without_end_date(self):
        """Tests that the end_date is defaulted if not provided when blacklisting from request"""
        fake_request = self.build_fake_request()
        instance = self.model_class.blacklist_from_request(fake_request)
        default_end_date = date.today() + timedelta(
            days=instance.get_default_duration()
        )
        assert instance.active
        assert instance.status == NetworkRule.Status.BLACKLISTED
        assert instance.expires_on == default_end_date

    @assert_logs(logger="security", level="INFO")
    def test_blacklist_from_request_override(self):
        """Tests that a whitelisted rule can be blacklisted only with the 'override' argument"""
        fake_request = self.build_fake_request()
        fake_ip_address = get_client_ip(fake_request)
        self.payload["ip"] = fake_ip_address
        self.payload["status"] = NetworkRule.Status.WHITELISTED
        self.model_class.objects.create(**self.payload)
        end_date = date.today() + timedelta(days=3)
        # Without override
        instance = self.model_class.blacklist_from_request(
            fake_request, end_date=end_date, override=False
        )
        assert not instance.active
        assert instance.status == NetworkRule.Status.WHITELISTED
        assert instance.expires_on == self.payload["expires_on"] != end_date
        # With override
        instance = self.model_class.blacklist_from_request(
            fake_request, end_date=end_date, override=True
        )
        assert instance.active
        assert instance.status == NetworkRule.Status.BLACKLISTED
        assert instance.expires_on == end_date

    @assert_logs(logger="security", level="INFO")
    def test_clear_from_request(self):
        """Tests 'clear_from_request' correctly resets the model fields"""
        fake_request = self.build_fake_request()
        fake_ip_address = get_client_ip(fake_request)
        self.payload["ip"] = fake_ip_address
        self.payload["active"] = True
        self.payload["status"] = NetworkRule.Status.BLACKLISTED
        self.payload["expires_on"] = date.today()
        self.model_class.objects.create(**self.payload)
        instance = self.model_class.clear_from_request(fake_request)
        assert not instance.active
        assert instance.status == NetworkRule.Status.NONE
        assert instance.expires_on is None

    @assert_logs(logger="security", level="INFO")
    def test_whitelist_from_request_general_behavior(self):
        """Tests the general behavior of the whitelist_from_request method"""
        fake_request = self.build_fake_request()
        new_comment = "Whitelisted"
        end_date = date.today() + timedelta(days=3)
        instance = self.model_class.whitelist_from_request(
            fake_request, end_date=end_date, comment=new_comment
        )
        assert instance.status == NetworkRule.Status.WHITELISTED
        assert instance.active
        assert instance.expires_on == end_date
        assert instance.comment == new_comment

    @assert_logs(logger="security", level="INFO")
    def test_whitelist_from_request_without_end_date(self):
        """Tests that the end_date is defaulted if not provided when whitelisting from request"""
        fake_request = self.build_fake_request()
        instance = self.model_class.whitelist_from_request(fake_request)
        default_end_date = date.today() + timedelta(
            days=instance.get_default_duration()
        )
        assert instance.active
        assert instance.status == NetworkRule.Status.WHITELISTED
        assert instance.expires_on == default_end_date

    @assert_logs(logger="security", level="INFO")
    def test_whitelist_from_request_override(self):
        """Tests that a blacklisted rule can be whitelisted only with the 'override' argument"""
        fake_request = self.build_fake_request()
        fake_ip_address = get_client_ip(fake_request)
        self.payload["ip"] = fake_ip_address
        self.payload["status"] = NetworkRule.Status.BLACKLISTED
        self.model_class.objects.create(**self.payload)
        end_date = date.today() + timedelta(days=3)
        # Without override
        instance = self.model_class.whitelist_from_request(
            fake_request, end_date=end_date, override=False
        )
        assert not instance.active
        assert instance.status == NetworkRule.Status.BLACKLISTED
        assert instance.expires_on == self.payload["expires_on"] != end_date
        # With override
        instance = self.model_class.whitelist_from_request(
            fake_request, end_date=end_date, override=True
        )
        assert instance.active
        assert instance.status == NetworkRule.Status.WHITELISTED
        assert instance.expires_on == end_date

    @assert_logs(logger="security", level="INFO")
    def test_is_blacklisted_from_request(self):
        """Tests that a blacklisted rule is correctly flagged as blacklisted"""
        fake_request = self.build_fake_request()
        fake_ip_address = get_client_ip(fake_request)
        self.payload["ip"] = fake_ip_address
        self.model_class.objects.create(**self.payload)
        self.model_class.blacklist_from_request(fake_request)
        assert self.model_class.is_blacklisted_from_request(fake_request)

    @assert_logs(logger="security", level="INFO")
    def test_is_whitelisted_from_request(self):
        """Tests that a whitelisted rule is correctly flagged as whitelisted"""
        fake_request = self.build_fake_request()
        fake_ip_address = get_client_ip(fake_request)
        self.payload["ip"] = fake_ip_address
        self.model_class.objects.create(**self.payload)
        self.model_class.whitelist_from_request(fake_request)
        assert self.model_class.is_whitelisted_from_request(fake_request)

    # ----------------------------------------
    # Signals
    # ----------------------------------------
    @assert_logs(logger="security", level="INFO")
    def test_log_signals(self):
        """Tests that logs are generated on creation, update, and deletion"""
        logs = self.logger_context.output
        instance = self.model_class.objects.create(**self.payload)
        assert logs[0] == self._build_log_message(instance, "created")
        instance.save()
        assert logs[1] == self._build_log_message(instance, "updated")
        instance.delete()
        assert logs[2] == self._build_log_message(instance, "deleted")

    # ----------------------------------------
    # Cron tests
    # ----------------------------------------
    @assert_logs(logger="security", level="INFO")
    def test_clear_expired_entries(self):
        """Tests that only the eligible entries are correctly cleared"""
        payloads, instances, clear_eligibility = self._create_instances_for_clear_test()
        NetworkRule.clear_expired_entries()
        for payload, instance, cleared in zip(payloads, instances, clear_eligibility):
            if cleared:
                updated_instance = self.model_class.objects.get(pk=instance.id)
                assert updated_instance.expires_on is None
                assert not updated_instance.active
                assert updated_instance.status == NetworkRule.Status.NONE
            else:
                assert instance.expires_on == payload["expires_on"]
                assert instance.active == payload["active"]
                assert instance.status == payload["status"]

    # ----------------------------------------
    # Helpers
    # ----------------------------------------
    @staticmethod
    def _build_log_message(instance, type_):
        """
        Generate the expected log message for an action on an NetworkRule
        :param NetworkRule instance: Any NetworkRule instance
        :param str type_: Should be 'created', 'updated', or 'deleted'
        :return: The expected log message
        :rtype: str
        """
        return f"INFO:security:NetworkRule {type_} for {instance.ip} (Status: {instance.computed_status})"

    def _create_instances_for_clear_test(self):
        """
        Builds various NetworkRule instances to test various scenarios for the clearing cron job later on
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
            ("127.0.0.1", NetworkRule.Status.NONE, None, False, False),
            ("127.0.0.2", NetworkRule.Status.BLACKLISTED, expired_date, True, True),
            ("127.0.0.3", NetworkRule.Status.WHITELISTED, None, False, False),
            ("127.0.0.4", NetworkRule.Status.BLACKLISTED, valid_date, True, False),
            ("127.0.0.5", NetworkRule.Status.WHITELISTED, expired_date, True, True),
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
