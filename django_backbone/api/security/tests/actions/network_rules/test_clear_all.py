"""TestCase for the 'clear_all' action"""

# Built-in
from datetime import date, timedelta

# Personal
from jklib.django.drf.tests import ActionTestCase
from jklib.django.utils.tests import assert_logs

# Local
from ....models import NetworkRule
from ._shared import (
    SERVICE_URL,
    assert_admin_permissions,
    assert_valid_status,
    create_network_rule,
)


# --------------------------------------------------------------------------------
# > TestCase
# --------------------------------------------------------------------------------
class TestClearAllNetworkRules(ActionTestCase):
    """TestCase for the 'clear_all' action"""

    service_base_url = f"{SERVICE_URL}/clear_all/"
    valid_status_code = 204
    RULE_QUANTITY = 3

    # ----------------------------------------
    # Behavior
    # ----------------------------------------
    @assert_logs("security", "INFO")
    def setUp(self):
        """Creates and authenticates an Admin user and generates a bunch of NetworkRule instances"""
        self.admin = self.create_admin_user(authenticate=True)
        self.payload = {"status": None}
        self._generate_all_instances()

    # ----------------------------------------
    # Tests
    # ----------------------------------------
    @assert_logs("security", "INFO")
    def test_permissions(self):
        """Tests that only admin users can access this service"""
        user = self.create_user()
        assert_admin_permissions(
            client=self.client,
            protocol=self.client.post,
            url=self.service_base_url,
            payload=self.payload,
            valid_status_code=self.valid_status_code,
            admin=self.admin,
            user=user,
        )

    @assert_logs("security", "INFO")
    def test_valid_status(self):
        """Tests that you must provide a valid status"""
        assert_valid_status(
            protocol=self.client.post,
            url=self.service_base_url,
            payload=self.payload,
            valid_status_code=self.valid_status_code,
            clean_up=False,
        )

    @assert_logs("security", "INFO")
    def test_status_optional(self):
        """Tests that you can omit the status field"""
        # Empty status
        self.payload["status"] = ""
        response = self.client.post(self.service_base_url, data=self.payload)
        assert response.status_code == self.valid_status_code
        # None status
        self.payload["status"] = None
        response = self.client.post(self.service_base_url, data=self.payload)
        assert response.status_code == self.valid_status_code

    @assert_logs("security", "INFO")
    def test_success_clear_all(self):
        """Tests that all NetworkRule instances are cleared if no status is provided"""
        response = self.client.post(self.service_base_url, data=self.payload)
        assert response.status_code == self.valid_status_code
        ids = (
            self.blacklisted_ids
            + self.whitelisted_ids
            + self.cleared_ids
            + self.neutral_ids
        )
        self._assert_rules_are_cleared(ids)

    @assert_logs("security", "INFO")
    def test_success_clear_blacklisted(self):
        """Tests that only our blacklisted rules get cleared"""
        self.payload["status"] = "BLACKLISTED"
        response = self.client.post(self.service_base_url, data=self.payload)
        assert response.status_code == self.valid_status_code
        self._assert_rules_are_cleared(self.blacklisted_ids + self.cleared_ids)
        self._assert_rules_are_not_cleared(self.whitelisted_ids + self.neutral_ids)

    @assert_logs("security", "INFO")
    def test_success_clear_whitelisted(self):
        """Tests that only our whitelisted rules get cleared"""
        self.payload["status"] = "WHITELISTED"
        response = self.client.post(self.service_base_url, data=self.payload)
        assert response.status_code == self.valid_status_code
        self._assert_rules_are_cleared(self.whitelisted_ids + self.cleared_ids)
        self._assert_rules_are_not_cleared(self.blacklisted_ids + self.neutral_ids)

    @assert_logs("security", "INFO")
    def test_success_clear_neutral(self):
        """Tests that only our 'NONE' rules get cleared"""
        self.payload["status"] = "NONE"
        response = self.client.post(self.service_base_url, data=self.payload)
        assert response.status_code == self.valid_status_code
        self._assert_rules_are_cleared(self.neutral_ids + self.cleared_ids)
        self._assert_rules_are_not_cleared(self.blacklisted_ids + self.whitelisted_ids)

    @assert_logs("security", "INFO")
    def test_success_nothing_to_clear(self):
        """Tests that the service returns a 204 even if no rule is found or eligible"""
        # No rule
        NetworkRule.objects.all().delete()
        self.payload["status"] = "BLACKLISTED"
        response = self.client.post(self.service_base_url, data=self.payload)
        assert response.status_code == self.valid_status_code
        assert NetworkRule.objects.count() == 0
        # No rule eligible based on our payload
        network_rule = create_network_rule()
        network_rule.whitelist()
        response = self.client.post(self.service_base_url, data=self.payload)
        assert response.status_code == self.valid_status_code
        self._assert_rules_are_not_cleared([network_rule.id])

    # ----------------------------------------
    # Private
    # ----------------------------------------
    @staticmethod
    def _assert_rules_are_cleared(ids):
        """
        Checks that the NetworkRule instances are cleared
        :param [int] ids: Id of the NetworkRule instances to check
        """
        instances = NetworkRule.objects.filter(pk__in=ids)
        for instance in instances:
            assert instance.expires_on is None
            assert not instance.active
            assert instance.status == NetworkRule.Status.NONE

    @staticmethod
    def _assert_rules_are_not_cleared(ids):
        """
        Checks that the NetworkRule instances are not cleared
        :param [int] ids: Id of the NetworkRule instances to check
        """
        instances = NetworkRule.objects.filter(pk__in=ids)
        for instance in instances:
            assert (
                instance.expires_on is not None
                or instance.active
                or instance.status != NetworkRule.Status.NONE
            )

    def _generate_all_instances(self):
        """Generates various NetworkRule instances for testing purposes and stores their IDs"""
        end_date = date.today() + timedelta(days=60)
        self.blacklisted_ids = self._generate_instances(
            status=NetworkRule.Status.BLACKLISTED,
            expires_on=end_date,
            active=True,
            ip_start=1,
            quantity=self.RULE_QUANTITY,
        )
        self.cleared_ids = self._generate_instances(
            status=NetworkRule.Status.NONE,
            expires_on=None,
            active=False,
            ip_start=2,
            quantity=self.RULE_QUANTITY,
        )
        self.neutral_ids = self._generate_instances(
            status=NetworkRule.Status.NONE,
            expires_on=end_date,
            active=True,
            ip_start=3,
            quantity=self.RULE_QUANTITY,
        )
        self.whitelisted_ids = self._generate_instances(
            status=NetworkRule.Status.WHITELISTED,
            expires_on=end_date,
            active=True,
            ip_start=4,
            quantity=self.RULE_QUANTITY,
        )

    @staticmethod
    def _generate_instances(status, expires_on, active, ip_start, quantity):
        """
        Generates a bunch of NetworkRule instances with the given parameters and returns their IDs
        :param Status status: The status enum for the NetworkRule
        :param expires_on: The expiration date for the status
        :type expires_on: date or None
        :param bool active: Whether the rule is active
        :param ip_start: The first part of the IP, to avoid duplicate/conflicts
        :type ip_start: int or str
        :param int quantity: The number of NetworkRule instance to create
        :return: The list of IDs for the created instances
        :rtype: [int]
        """
        payload = {
            "status": status,
            "expires_on": expires_on,
            "active": active,
        }
        instances = []
        for i in range(quantity):
            payload["ip"] = f"{ip_start}.0.0.{i + 1}"
            instance = create_network_rule(**payload)
            instances.append(instance)
        return [instance.id for instance in instances]
