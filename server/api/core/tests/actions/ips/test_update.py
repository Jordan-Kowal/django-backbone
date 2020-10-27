"""TestCase for the 'update' action"""

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
    assert_representation_matches_instance,
    create_ip_address,
)


# --------------------------------------------------------------------------------
# > TestCase
# --------------------------------------------------------------------------------
class TestUpdateIp(ActionTestCase):
    """TestCase for the 'update' action"""

    required_fields = ["ip", "status"]
    service_base_url = f"{SERVICE_URL}/"

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
        # 401 Unauthenticated
        self.client.logout()
        response = self.client.put(self.ip_detail_url, data=self.payload)
        assert response.status_code == 401
        # 403 Not admin
        self.create_user(authenticate=True)
        response = self.client.put(self.ip_detail_url, data=self.payload)
        assert response.status_code == 403
        # 201 Admin
        self.client.logout()
        self.client.force_authenticate(self.admin)
        response = self.client.put(self.ip_detail_url, data=self.payload)
        assert response.status_code == 200

    def test_required_fields(self):
        """Tests that required fields are truly required"""
        self.assert_fields_are_required(
            self.client.put, self.ip_detail_url, self.payload
        )

    def test_unknown_ip_address(self):
        """Tests that we cannot update an unknown IP"""
        unknown_url = self.detail_url(10)
        # Admin should get 404
        response = self.client.put(unknown_url, data=self.payload)
        assert response.status_code == 404
        # User should get 403
        self.client.logout()
        self.create_user(authenticate=True)
        response = self.client.put(unknown_url, data=self.payload)
        assert response.status_code == 403

    def test_valid_expires_on(self):
        """Tests that you must provide a valid date in format and value"""
        # Invalid dates
        past_date = (date.today() - timedelta(days=1)).strftime("%Y-%m-%d")
        invalid_format_date = (date.today() - timedelta(days=1)).strftime("%Y-%d")
        for date_value in [past_date, invalid_format_date]:
            self.payload["expires_on"] = date_value
            response = self.client.put(self.ip_detail_url, data=self.payload)
            self.assert_field_has_error(response, "expires_on")
        # Valid dates
        raw_date = date.today() + timedelta(days=1)
        formatted_date = raw_date.strftime("%Y-%m-%d")
        for date_value in [raw_date, formatted_date]:
            self.payload["expires_on"] = date_value
            response = self.client.put(self.ip_detail_url, data=self.payload)
            assert response.status_code == 200

    def test_valid_status(self):
        """Tests that you must provide a valid status"""
        # Invalid statuses
        unknown_integer = 999
        unknown_string = "TEST"
        unsupported_value = 3.3
        for status in [unknown_integer, unknown_string, unsupported_value]:
            self.payload["status"] = status
            response = self.client.put(self.ip_detail_url, data=self.payload)
            self.assert_field_has_error(response, "status")
        # Valid statuses
        status_as_integer = 1
        status_as_string = "WHITELISTED"
        for status in [status_as_integer, status_as_string]:
            self.payload["status"] = status
            response = self.client.put(self.ip_detail_url, data=self.payload)
            assert response.status_code == 200

    def test_comment_length(self):
        """Tests that the comment cannot exceed the max length"""
        self.payload["comment"] = "a" * (IpAddress.COMMENT_MAX_LENGTH + 1)
        response = self.client.put(self.ip_detail_url, data=self.payload)
        self.assert_field_has_error(response, "comment")

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
        assert response.status_code == 200
        ip_address = IpAddress.objects.get(pk=1)
        assert_representation_matches_instance(response.data, ip_address)
