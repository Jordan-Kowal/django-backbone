"""TestCase for the 'blacklist_existing' action"""


# Built-in
from datetime import date, timedelta

# Django
from django.conf import settings
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
class TestBlacklistExistingIp(ActionTestCase):
    """TestCase for the 'blacklist_existing' action"""

    service_base_url = f"{SERVICE_URL}/"
    service_extra_url = "blacklist/"

    # ----------------------------------------
    # Behavior
    # ----------------------------------------
    @classmethod
    def setUpClass(cls):
        """Sets up the API client"""
        cls.client = APIClient()

    def setUp(self):
        """Creates and authenticates an Admin user, and creates 1 IpAddress instance and a payload"""
        self.admin = self.create_admin_user(authenticate=True)
        self.ip = create_ip_address()
        self.ip_url = self.detail_url(self.ip.id)
        self.default_payload = {
            "expires_on": None,
            "comment": "Test comment",
            "override": False,
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
        """Tests that only admin user can retrieve an IP"""
        # 401 Unauthenticated
        self.client.logout()
        response = self.client.post(self.ip_url)
        assert response.status_code == 401
        # 403 Not admin
        self.create_user(authenticate=True)
        response = self.client.post(self.ip_url)
        assert response.status_code == 403
        # 201 Admin
        self.client.logout()
        self.client.force_authenticate(self.admin)
        response = self.client.post(self.ip_url)
        assert response.status_code == 200

    def test_unknown_ip_address(self):
        """Tests that we cannot fetch an unknown IP"""
        unknown_url = self.detail_url(10)
        # Admin should get 404
        response = self.client.post(unknown_url)
        assert response.status_code == 404
        # User should get 403
        self.client.logout()
        self.create_user(authenticate=True)
        response = self.client.post(unknown_url)
        assert response.status_code == 403

    def test_comment_length(self):
        """Tests that the comment has a length limit"""
        # Too long should fail
        self.default_payload["comment"] = "a" * (IpAddress.COMMENT_MAX_LENGTH + 1)
        response = self.client.post(self.ip_url, data=self.default_payload)
        self.assert_field_has_error(response, "comment")
        # Long enough
        self.default_payload["comment"] = "a" * IpAddress.COMMENT_MAX_LENGTH
        response = self.client.post(self.ip_url, data=self.default_payload)
        assert response.status_code == 200

    def test_expires_on_optional(self):
        """Tests that the 'expires_on' gets defaulted if not provided"""
        # With a given date
        expiration_date = (date.today() + timedelta(days=100)).strftime("%Y-%m-%d")
        self.default_payload["expires_on"] = expiration_date
        response = self.client.post(self.ip_url, data=self.default_payload)
        assert response.status_code == 200
        updated_ip = IpAddress.objects.get(pk=self.ip.id)
        assert updated_ip.expires_on.strftime("%Y-%m-%d") == expiration_date
        # Without date
        self.default_payload["expires_on"] = None
        response = self.client.post(self.ip_url, data=self.default_payload)
        assert response.status_code == 200
        updated_ip = IpAddress.objects.get(pk=self.ip.id)
        expected_date = date.today() + timedelta(
            days=settings.IP_STATUS_DEFAULT_DURATION
        )
        assert updated_ip.expires_on == expected_date

    def test_valid_expires_on(self):
        """Tests that you must provide a valid date in format and value"""
        # Invalid dates
        past_date = (date.today() - timedelta(days=1)).strftime("%Y-%m-%d")
        invalid_format_date = (date.today() - timedelta(days=1)).strftime("%Y-%d")
        for date_value in [past_date, invalid_format_date]:
            self.default_payload["expires_on"] = date_value
            response = self.client.post(self.ip_url, data=self.default_payload)
            self.assert_field_has_error(response, "expires_on")
        # Valid dates
        raw_date = date.today() + timedelta(days=1)
        formatted_date = raw_date.strftime("%Y-%m-%d")
        for date_value in [raw_date, formatted_date]:
            self.default_payload["expires_on"] = date_value
            response = self.client.post(self.ip_url, data=self.default_payload)
            assert response.status_code == 200

    def test_override_on_whitelisted(self):
        """Tests that a whitelisted IP can be blacklisted only with 'override=True'"""
        second_ip = create_ip_address(ip="127.0.0.2")
        second_ip_url = self.detail_url(second_ip.id)
        second_ip.whitelist()
        # Whitelisted without override
        response = self.client.post(second_ip_url, data=self.default_payload)
        self.assert_field_has_error(response, "override")
        # With override
        self.default_payload["override"] = True
        response = self.client.post(second_ip_url, data=self.default_payload)
        assert response.status_code == 200
        updated_ip = IpAddress.objects.get(pk=second_ip.id)
        assert updated_ip.status == IpAddress.IpStatus.BLACKLISTED

    def test_blacklist_success(self):
        """Tests that we can successfully blacklist an existing IP"""
        assert not self.ip.is_blacklisted
        response = self.client.post(self.ip_url)
        assert response.status_code == 200
        updated_instance = IpAddress.objects.get(pk=self.ip.id)
        assert updated_instance.is_blacklisted
        assert_representation_matches_instance(response.data, updated_instance)
