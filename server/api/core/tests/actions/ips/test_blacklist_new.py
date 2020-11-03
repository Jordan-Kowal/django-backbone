"""TestCase for the 'blacklist_new' action"""


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
    assert_expires_on_is_optional,
    assert_representation_matches_instance,
    assert_unique_ip_on_creation,
    assert_valid_expires_on,
)


# --------------------------------------------------------------------------------
# > TestCase
# --------------------------------------------------------------------------------
class TestBlacklistNewIp(ActionTestCase):
    """TestCase for the 'blacklist_new' action"""

    required_fields = ["ip"]
    service_base_url = f"{SERVICE_URL}/blacklist/"
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
            "expires_on": None,
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
            self.client,
            self.client.post,
            self.service_base_url,
            self.payload,
            self.valid_status_code,
            self.admin,
            user,
        )
        assert IpAddress.objects.count() == 1

    def test_required_fields(self):
        """Tests that the required fields are truly required"""
        self.assert_fields_are_required(
            self.client.post, self.service_base_url, self.payload
        )
        assert IpAddress.objects.count() == 0

    def test_unique_ip(self):
        """Tests that you cannot create the same IP twice"""
        assert_unique_ip_on_creation(
            protocol=self.client.post,
            url=self.service_base_url,
            payload=self.payload,
            valid_status_code=self.valid_status_code,
            count=0,
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

    def test_expires_on_optional(self):
        """Tests that the 'expires_on' gets defaulted if not provided"""
        assert_expires_on_is_optional(
            protocol=self.client.post,
            url=self.service_base_url,
            payload=self.payload,
            valid_status_code=self.valid_status_code,
            id_=1,
            creation=True,
        )

    def test_valid_expires_on(self):
        """Tests that you must provide a valid date in format and value"""
        assert_valid_expires_on(
            protocol=self.client.post,
            url=self.service_base_url,
            payload=self.payload,
            valid_status_code=self.valid_status_code,
            clean_up=True,
        )

    def test_blacklist_success(self):
        """Tests that we can successfully create and blacklist an IP"""
        response = self.client.post(self.service_base_url, data=self.payload)
        assert response.status_code == self.valid_status_code
        assert IpAddress.objects.count() == 1
        created_instance = IpAddress.objects.get(pk=response.data["id"])
        assert created_instance.is_blacklisted
        assert_representation_matches_instance(response.data, created_instance)
