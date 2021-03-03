"""TestCase for the 'create' action"""

# Personal
from jklib.django.drf.tests import ActionTestCase

# Local
from ....models import NetworkRule
from ._shared import (
    SERVICE_URL,
    assert_admin_permissions,
    assert_comment_length,
    assert_representation_matches_instance,
    assert_unique_constraint_on_creation,
    assert_valid_expires_on,
    assert_valid_status,
)


# --------------------------------------------------------------------------------
# > TestCase
# --------------------------------------------------------------------------------
class TestCreateNetworkRule(ActionTestCase):
    """TestCase for the 'create' action"""

    required_fields = ["ip", "status"]
    service_base_url = f"{SERVICE_URL}/"
    valid_status_code = 201

    # ----------------------------------------
    # Behavior
    # ----------------------------------------
    def setUp(self):
        """Creates and authenticates an Admin user, and prepares a valid payload"""
        self.admin = self.create_admin_user(authenticate=True)
        self.payload = {
            "ip": "127.0.0.1",
            "status": "WHITELISTED",
            "expires_on": None,
            "active": False,
            "comment": "Test comment",
        }

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
        assert NetworkRule.objects.count() == 1

    def test_required_fields(self):
        """Tests that required fields are truly required"""
        self.assert_fields_are_required(
            self.client.post, self.service_base_url, self.payload
        )
        assert NetworkRule.objects.count() == 0

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
        assert NetworkRule.objects.count() == 1

    def test_unique_constraint(self):
        """Tests that you cannot create two NetworkRule instances with the same IP"""
        assert_unique_constraint_on_creation(
            protocol=self.client.post,
            url=self.service_base_url,
            payload=self.payload,
            valid_status_code=self.valid_status_code,
            count=0,
        )

    def test_create_success(self):
        """Tests that we created a new NetworkRule successfully"""
        response = self.client.post(self.service_base_url, data=self.payload)
        assert response.status_code == 201
        assert NetworkRule.objects.count() == 1
        network_rule = NetworkRule.objects.get(pk=1)
        assert_representation_matches_instance(response.data, network_rule)
