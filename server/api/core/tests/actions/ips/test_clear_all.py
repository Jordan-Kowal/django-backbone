"""TestCase for the 'clear_all' action"""

# Built-in
from datetime import date, timedelta

# Django
from rest_framework.test import APIClient

# Personal
from jklib.django.drf.tests import ActionTestCase

# Local
from ....models import IpAddress
from ._shared import (
    SERVICE_URL,
    assert_admin_permissions,
    assert_valid_status,
    create_ip_address,
)


# --------------------------------------------------------------------------------
# > TestCase
# --------------------------------------------------------------------------------
class TestClearAllIps(ActionTestCase):
    """TestCase for the 'clear_all' action"""

    service_base_url = f"{SERVICE_URL}/clear_all/"
    valid_status_code = 204
    IP_QUANTITY = 3

    # ----------------------------------------
    # Behavior
    # ----------------------------------------
    @classmethod
    def setUpClass(cls):
        """Sets up the API client"""
        cls.client = APIClient()

    def setUp(self):
        """Creates and authenticates an Admin user and generates a bunch of IpAddress instances"""
        self.admin = self.create_admin_user(authenticate=True)
        self.payload = {"status": None}
        self._generate_all_ips()

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

    def test_valid_status(self):
        """Tests that you must provide a valid status"""
        assert_valid_status(
            protocol=self.client.post,
            url=self.service_base_url,
            payload=self.payload,
            valid_status_code=self.valid_status_code,
            clean_up=False,
        )

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

    def test_success_clear_all(self):
        """Tests that all IPs are cleared if no status is provided"""
        response = self.client.post(self.service_base_url, data=self.payload)
        assert response.status_code == self.valid_status_code
        ips = (
            self.blacklisted_ids
            + self.whitelisted_ids
            + self.cleared_ids
            + self.neutral_ids
        )
        self._assert_ips_are_cleared(ips)

    def test_success_clear_blacklisted(self):
        """Tests that only our blacklisted IPs get cleared"""
        self.payload["status"] = "BLACKLISTED"
        response = self.client.post(self.service_base_url, data=self.payload)
        assert response.status_code == self.valid_status_code
        self._assert_ips_are_cleared(self.blacklisted_ids + self.cleared_ids)
        self._assert_ips_are_not_cleared(self.whitelisted_ids + self.neutral_ids)

    def test_success_clear_whitelisted(self):
        """Tests that only our whitelisted IPs get cleared"""
        self.payload["status"] = "WHITELISTED"
        response = self.client.post(self.service_base_url, data=self.payload)
        assert response.status_code == self.valid_status_code
        self._assert_ips_are_cleared(self.whitelisted_ids + self.cleared_ids)
        self._assert_ips_are_not_cleared(self.blacklisted_ids + self.neutral_ids)

    def test_success_clear_neutral(self):
        """Tests that only our 'NONE' IPs get cleared"""
        self.payload["status"] = "NONE"
        response = self.client.post(self.service_base_url, data=self.payload)
        assert response.status_code == self.valid_status_code
        self._assert_ips_are_cleared(self.neutral_ids + self.cleared_ids)
        self._assert_ips_are_not_cleared(self.blacklisted_ids + self.whitelisted_ids)

    def test_success_nothing_to_clear(self):
        """Tests that the service returns a 204 even if no IP is found or eligible"""
        # No IP
        IpAddress.objects.all().delete()
        self.payload["status"] = "BLACKLISTED"
        response = self.client.post(self.service_base_url, data=self.payload)
        assert response.status_code == self.valid_status_code
        assert IpAddress.objects.count() == 0
        # No IP eligible based on our payload
        ip = create_ip_address()
        ip.whitelist()
        response = self.client.post(self.service_base_url, data=self.payload)
        assert response.status_code == self.valid_status_code
        self._assert_ips_are_not_cleared([ip.id])

    # ----------------------------------------
    # Private
    # ----------------------------------------
    @staticmethod
    def _assert_ips_are_cleared(ids):
        """
        Checks that the IpAddress instances are cleared
        :param [int] ids: Id of the IpAddress instances to check
        """
        instances = IpAddress.objects.filter(pk__in=ids)
        for instance in instances:
            assert instance.expires_on is None
            assert not instance.active
            assert instance.status == IpAddress.IpStatus.NONE

    @staticmethod
    def _assert_ips_are_not_cleared(ids):
        """
        Checks that the IpAddress instances are not cleared
        :param [int] ids: Id of the IpAddress instances to check
        """
        instances = IpAddress.objects.filter(pk__in=ids)
        for instance in instances:
            assert (
                instance.expires_on is not None
                or instance.active
                or instance.status != IpAddress.IpStatus.NONE
            )

    def _generate_all_ips(self):
        """Generates various IpAddress instances for testing purposes and stores their IDs"""
        end_date = date.today() + timedelta(days=60)
        self.blacklisted_ids = self._generate_ips(
            status=IpAddress.IpStatus.BLACKLISTED,
            expires_on=end_date,
            active=True,
            ip_start=1,
            quantity=self.IP_QUANTITY,
        )
        self.cleared_ids = self._generate_ips(
            status=IpAddress.IpStatus.NONE,
            expires_on=None,
            active=False,
            ip_start=2,
            quantity=self.IP_QUANTITY,
        )
        self.neutral_ids = self._generate_ips(
            status=IpAddress.IpStatus.NONE,
            expires_on=end_date,
            active=True,
            ip_start=3,
            quantity=self.IP_QUANTITY,
        )
        self.whitelisted_ids = self._generate_ips(
            status=IpAddress.IpStatus.WHITELISTED,
            expires_on=end_date,
            active=True,
            ip_start=4,
            quantity=self.IP_QUANTITY,
        )

    @staticmethod
    def _generate_ips(status, expires_on, active, ip_start, quantity):
        """
        Generates a bunch of IPs with the given parameters and returns their IDs
        :param IpStatus status: The status enum for the IP
        :param expires_on: The expiration date for the status
        :type expires_on: date or None
        :param bool active: Whether the ip is active
        :param ip_start: The first part of the IP, to avoid duplicate/conflicts
        :type ip_start: int or str
        :param int quantity: The number of IpAddress instance to create
        :return: The list of IDs for the created instances
        :rtype: [int]
        """
        payload = {
            "status": status,
            "expires_on": expires_on,
            "active": active,
        }
        ips = []
        for i in range(quantity):
            payload["ip"] = f"{ip_start}.0.0.{i + 1}"
            instance = create_ip_address(**payload)
            ips.append(instance)
        return [instance.id for instance in ips]
