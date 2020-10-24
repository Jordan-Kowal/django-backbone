"""TestCase for the 'create' action"""

# Built-in
from datetime import date, timedelta

# Django
from rest_framework.test import APIClient

# Personal
from jklib.django.drf.tests import ActionTestCase

# Local
from ....models import IpAddress
from ._shared import SERVICE_URL, assert_representation_matches_instance


# --------------------------------------------------------------------------------
# > TestCase
# --------------------------------------------------------------------------------
class TestCreateIp(ActionTestCase):
    """TestCase for the 'create' action"""

    required_fields = ["ip", "status", "expires_on"]
    service_base_url = f"{SERVICE_URL}/"

    # ----------------------------------------
    # Behavior
    # ----------------------------------------
    @classmethod
    def setUpClass(cls):
        """Sets up the API client"""
        cls.client = APIClient()

    def setUp(self):
        """Creates and authenticates an Admin user, and prepare a valid payload"""
        self.admin = self.create_admin_user(authenticate=True)
        expiration_date = date.today() + timedelta(days=1)
        self.payload = {
            "ip": "127.0.0.1",
            "status": "WHITELISTED",
            "expires_on": expiration_date.strftime("%Y-%m-%d"),
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
        response = self.client.post(self.service_base_url, data=self.payload)
        assert response.status_code == 401
        assert IpAddress.objects.count() == 0
        # 403 Not admin
        self.create_user(authenticate=True)
        response = self.client.post(self.service_base_url, data=self.payload)
        assert response.status_code == 403
        assert IpAddress.objects.count() == 0
        # 201 Admin
        self.client.logout()
        self.client.force_authenticate(self.admin)
        response = self.client.post(self.service_base_url, data=self.payload)
        assert response.status_code == 201
        assert IpAddress.objects.count() == 1

    def test_required_fields(self):
        """Tests that required fields are truly required"""
        self.client.force_authenticate(self.admin)
        self.assert_fields_are_required(
            self.client.post, self.service_base_url, self.payload
        )
        assert IpAddress.objects.count() == 0

    def test_valid_expires_on(self):
        """Tests that you must provide a valid date in format and value"""
        # Invalid dates
        past_date = (date.today() - timedelta(days=1)).strftime("%Y-%m-%d")
        invalid_format_date = (date.today() - timedelta(days=1)).strftime("%Y-%d")
        for date_value in [past_date, invalid_format_date]:
            self.payload["expires_on"] = date_value
            response = self.client.post(self.service_base_url, data=self.payload)
            self.assert_field_has_error(response, "expires_on")
        assert IpAddress.objects.count() == 0
        # Valid dates
        raw_date = date.today() + timedelta(days=1)
        formatted_date = raw_date.strftime("%Y-%m-%d")
        for date_value in [raw_date, formatted_date]:
            self.payload["expires_on"] = date_value
            response = self.client.post(self.service_base_url, data=self.payload)
            assert response.status_code == 201
            assert IpAddress.objects.count() == 1
            IpAddress.objects.all().delete()

    def test_valid_status(self):
        """Tests that you must provide a valid status"""
        # Invalid statuses
        unknown_integer = 999
        unknown_string = "TEST"
        unsupported_value = 3.3
        for status in [unknown_integer, unknown_string, unsupported_value]:
            self.payload["status"] = status
            response = self.client.post(self.service_base_url, data=self.payload)
            self.assert_field_has_error(response, "status")
        # Valid statuses
        status_as_integer = 1
        status_as_string = "WHITELISTED"
        for status in [status_as_integer, status_as_string]:
            self.payload["status"] = status
            response = self.client.post(self.service_base_url, data=self.payload)
            assert response.status_code == 201
            assert IpAddress.objects.count() == 1
            IpAddress.objects.all().delete()

    def test_comment_length(self):
        """Tests that the comment cannot exceed the max length"""
        self.payload["comment"] = "a" * (IpAddress.COMMENT_MAX_LENGTH + 1)
        response = self.client.post(self.service_base_url, data=self.payload)
        self.assert_field_has_error(response, "comment")
        assert IpAddress.objects.count() == 0

    def test_unique_ip(self):
        """Tests that you cannot create the same IP twice"""
        # First should succeed
        response = self.client.post(self.service_base_url, data=self.payload)
        assert response.status_code == 201
        assert IpAddress.objects.count() == 1
        # Second should fail
        response = self.client.post(self.service_base_url, data=self.payload)
        assert response.status_code == 400
        assert IpAddress.objects.count() == 1

    def test_create_success(self):
        """Tests that we created an IP address successfully"""
        response = self.client.post(self.service_base_url, data=self.payload)
        assert response.status_code == 201
        assert IpAddress.objects.count() == 1
        ip_address = IpAddress.objects.get(pk=1)
        assert_representation_matches_instance(response.data, ip_address)
