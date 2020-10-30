"""TestCase for the 'update' action"""

# Django
from rest_framework.test import APIClient

# Personal
from jklib.django.drf.tests import ActionTestCase

# Local
from ....models import IpAddress
from ._shared import (
    SERVICE_URL,
    assert_admin_permissions,
    assert_comment_length,
    assert_representation_matches_instance,
    assert_unknown_ip,
    assert_valid_expires_on,
    assert_valid_status,
    create_ip_address,
)


# --------------------------------------------------------------------------------
# > TestCase
# --------------------------------------------------------------------------------
class TestUpdateIp(ActionTestCase):
    """TestCase for the 'update' action"""

    required_fields = ["ip", "status"]
    service_base_url = f"{SERVICE_URL}/"
    valid_status_code = 200

    # ----------------------------------------
    # Behavior
    # ----------------------------------------
    @classmethod
    def setUpClass(cls):
        """Sets up the API client"""
        cls.client = APIClient()

    def setUp(self):
        """
        Prepares the following elements
            Creates and authenticates an Admin user
            Creates 1 IpAddress
            Generates a re-usable payload
        """
        self.admin = self.create_admin_user(authenticate=True)
        self.ip = create_ip_address(ip="127.0.0.1")
        self.ip_detail_url = self.detail_url(self.ip.id)
        self.payload = {
            "ip": "128.0.0.1",
            "status": "WHITELISTED",
            "expires_on": None,
            "active": False,
            "comment": "Test comment",
        }

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
            protocol=self.client.put,
            url=self.ip_detail_url,
            payload=self.payload,
            valid_status_code=self.valid_status_code,
            admin=self.admin,
            user=user,
        )

    def test_required_fields(self):
        """Tests that required fields are truly required"""
        self.assert_fields_are_required(
            self.client.put, self.ip_detail_url, self.payload
        )

    def test_unknown_ip_address(self):
        """Tests that we cannot update an unknown IP"""
        unknown_url = self.detail_url(10)
        user = self.create_user()
        assert_unknown_ip(
            client=self.client,
            protocol=self.client.put,
            url=unknown_url,
            payload=self.payload,
            admin=self.admin,
            user=user,
        )

    def test_valid_expires_on(self):
        """Tests that you must provide a valid date in format and value"""
        assert_valid_expires_on(
            protocol=self.client.put,
            url=self.ip_detail_url,
            payload=self.payload,
            valid_status_code=self.valid_status_code,
            clean_up=False,
        )

    def test_valid_status(self):
        """Tests that you must provide a valid status"""
        assert_valid_status(
            protocol=self.client.put,
            url=self.ip_detail_url,
            payload=self.payload,
            valid_status_code=self.valid_status_code,
            clean_up=False,
        )

    def test_comment_length(self):
        """Tests that the comment cannot exceed the max length"""
        assert_comment_length(
            protocol=self.client.put,
            url=self.ip_detail_url,
            payload=self.payload,
            valid_status_code=self.valid_status_code,
        )

    def test_unique_ip(self):
        """Tests that you cannot update the IP to an existing one"""
        second_ip = create_ip_address(ip="127.0.0.2")
        detail_url = self.detail_url(second_ip.id)
        self.payload["ip"] = self.ip.ip
        response = self.client.put(detail_url, data=self.payload)
        assert response.status_code == 400

    def test_update_success(self):
        """Tests that we updated an IP address successfully"""
        response = self.client.put(self.ip_detail_url, data=self.payload)
        assert response.status_code == self.valid_status_code
        ip_address = IpAddress.objects.get(pk=1)
        assert_representation_matches_instance(response.data, ip_address)
