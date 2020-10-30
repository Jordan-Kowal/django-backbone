"""TestCase for the 'create' action"""

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
    assert_valid_expires_on,
    assert_valid_status,
)


# --------------------------------------------------------------------------------
# > TestCase
# --------------------------------------------------------------------------------
class TestCreateIp(ActionTestCase):
    """TestCase for the 'create' action"""

    required_fields = ["ip", "status"]
    service_base_url = f"{SERVICE_URL}/"
    valid_status_code = 201

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
        self.payload = {
            "ip": "127.0.0.1",
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
            protocol=self.client.post,
            url=self.service_base_url,
            payload=self.payload,
            valid_status_code=self.valid_status_code,
            admin=self.admin,
            user=user,
        )
        assert IpAddress.objects.count() == 1

    def test_required_fields(self):
        """Tests that required fields are truly required"""
        self.assert_fields_are_required(
            self.client.post, self.service_base_url, self.payload
        )
        assert IpAddress.objects.count() == 0

    def test_valid_expires_on(self):
        """Tests that you must provide a valid date in format and value"""
        assert_valid_expires_on(
            protocol=self.client.post,
            url=self.service_base_url,
            payload=self.payload,
            valid_status_code=self.valid_status_code,
            clean_up=True,
        )

    def test_valid_status_code(self):
        """Tests that you must provide a valid status"""
        assert_valid_status(
            protocol=self.client.post,
            url=self.service_base_url,
            payload=self.payload,
            valid_status_code=self.valid_status_code,
            clean_up=True,
        )

    def test_comment_length(self):
        """Tests that the comment cannot exceed the max length"""
        assert_comment_length(
            protocol=self.client.post,
            url=self.service_base_url,
            payload=self.payload,
            valid_status_code=self.valid_status_code,
        )
        assert IpAddress.objects.count() == 1

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
