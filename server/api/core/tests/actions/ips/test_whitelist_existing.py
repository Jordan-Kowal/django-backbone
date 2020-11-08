"""TestCase for the 'whitelist_existing' action"""


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
    assert_override_condition,
    assert_representation_matches_instance,
    assert_unknown_ip,
    assert_valid_expires_on,
    create_ip_address,
)


# --------------------------------------------------------------------------------
# > TestCase
# --------------------------------------------------------------------------------
class TestWhitelistExistingIp(ActionTestCase):
    """TestCase for the 'whitelist_existing' action"""

    service_base_url = f"{SERVICE_URL}/"
    service_extra_url = "whitelist/"
    valid_status_code = 200

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
        user = self.create_user()
        assert_admin_permissions(
            client=self.client,
            protocol=self.client.post,
            url=self.ip_url,
            payload=self.default_payload,
            valid_status_code=self.valid_status_code,
            admin=self.admin,
            user=user,
        )

    def test_unknown_ip(self):
        """Tests that we cannot whitelist an unknown IP"""
        unknown_url = self.detail_url(10)
        user = self.create_user()
        assert_unknown_ip(
            client=self.client,
            protocol=self.client.post,
            url=unknown_url,
            payload=self.default_payload,
            admin=self.admin,
            user=user,
        )

    def test_comment_length(self):
        """Tests that the comment has a length limit"""
        assert_comment_length(
            protocol=self.client.post,
            url=self.ip_url,
            payload=self.default_payload,
            valid_status_code=self.valid_status_code,
        )

    def test_expires_on_optional(self):
        """Tests that the 'expires_on' gets defaulted if not provided"""
        assert_expires_on_is_optional(
            protocol=self.client.post,
            url=self.ip_url,
            payload=self.default_payload,
            valid_status_code=self.valid_status_code,
            id_=self.ip.id,
        )

    def test_valid_expires_on(self):
        """Tests that you must provide a valid date in format and value"""
        assert_valid_expires_on(
            protocol=self.client.post,
            url=self.ip_url,
            payload=self.default_payload,
            valid_status_code=self.valid_status_code,
            clean_up=False,
        )

    def test_override_check(self):
        """Tests that a blacklisted IP can be whitelisted only with 'override=True'"""
        second_ip = create_ip_address(ip="127.0.0.2")
        second_ip_url = self.detail_url(second_ip.id)
        second_ip.blacklist()
        assert_override_condition(
            protocol=self.client.post,
            url=second_ip_url,
            payload=self.default_payload,
            valid_status_code=self.valid_status_code,
            id_=second_ip.id,
            ip_status=IpAddress.IpStatus.WHITELISTED,
        )

    def test_whitelist_success(self):
        """Tests that we can successfully blacklist an existing IP"""
        assert not self.ip.is_whitelisted
        response = self.client.post(self.ip_url)
        assert response.status_code == self.valid_status_code
        updated_instance = IpAddress.objects.get(pk=self.ip.id)
        assert updated_instance.is_whitelisted
        assert_representation_matches_instance(response.data, updated_instance)
