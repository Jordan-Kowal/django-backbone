"""TestCase for the 'blacklist_new' action"""

# Personal
from jklib.django.drf.tests import ActionTestCase
from jklib.django.utils.tests import assert_logs

# Local
from ....models import NetworkRule
from ._shared import (
    SERVICE_URL,
    assert_admin_permissions,
    assert_comment_length,
    assert_expires_on_is_optional,
    assert_representation_matches_instance,
    assert_unique_constraint_on_creation,
    assert_valid_expires_on,
)


# --------------------------------------------------------------------------------
# > TestCase
# --------------------------------------------------------------------------------
class TestNewBlacklistNetworkRule(ActionTestCase):
    """TestCase for the 'blacklist_new' action"""

    required_fields = ["ip"]
    service_base_url = f"{SERVICE_URL}/blacklist/"
    valid_status_code = 201

    # ----------------------------------------
    # Behavior
    # ----------------------------------------
    def setUp(self):
        """Creates and authenticates an Admin user, and prepare a valid payload"""
        self.admin = self.create_admin_user(authenticate=True)
        self.payload = {
            "ip": "127.0.0.10",
            "expires_on": None,
            "comment": "Test comment",
        }

    # ----------------------------------------
    # Tests
    # ----------------------------------------\
    @assert_logs("security", "INFO")
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
        assert NetworkRule.objects.count() == 1

    def test_required_fields(self):
        """Tests that the required fields are truly required"""
        self.assert_fields_are_required(
            self.client.post, self.service_base_url, self.payload
        )
        assert NetworkRule.objects.count() == 0

    def test_unique_constraint(self):
        """Tests that you cannot create the same IP twice"""
        assert_unique_constraint_on_creation(
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
        assert NetworkRule.objects.count() == 1

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
        assert NetworkRule.objects.count() == 1
        created_instance = NetworkRule.objects.get(pk=response.data["id"])
        assert created_instance.is_blacklisted
        assert_representation_matches_instance(response.data, created_instance)
