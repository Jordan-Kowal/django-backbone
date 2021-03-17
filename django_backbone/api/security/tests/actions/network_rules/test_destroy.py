"""TestCase for the 'destroy' action"""

# Personal
from jklib.django.drf.tests import ActionTestCase

# Local
from ....models import NetworkRule
from ._shared import (
    SERVICE_URL,
    assert_admin_permissions,
    assert_unknown_instance,
    create_network_rule,
)


# --------------------------------------------------------------------------------
# > TestCase
# --------------------------------------------------------------------------------
class TestDestroyNetworkRule(ActionTestCase):
    """TestCase for the 'destroy' action"""

    service_base_url = f"{SERVICE_URL}/"
    valid_status_code = 204

    # ----------------------------------------
    # Behavior
    # ----------------------------------------
    def setUp(self):
        """Creates and authenticates an admin user and creates 2 NetworkRule instances"""
        self.admin = self.create_admin_user(authenticate=True)
        self.first_rule = create_network_rule()
        self.first_rule_url = self.detail_url(self.first_rule.id)
        self.second_rule = create_network_rule(ip="127.0.0.2")
        self.second_rule_url = self.detail_url(self.second_rule.id)

    # ----------------------------------------
    # Tests
    # ----------------------------------------
    def test_permissions(self):
        """Tests that only admin users can use this service"""
        user = self.create_user()
        assert_admin_permissions(
            client=self.client,
            protocol=self.client.delete,
            url=self.first_rule_url,
            payload=None,
            valid_status_code=self.valid_status_code,
            admin=self.admin,
            user=user,
        )
        assert NetworkRule.objects.count() == 1

    def test_unknown_instance(self):
        """Tests that you get an error when trying to delete an unknown object"""
        unknown_url = self.detail_url(10)
        user = self.create_user()
        assert_unknown_instance(
            client=self.client,
            protocol=self.client.delete,
            url=unknown_url,
            payload=None,
            admin=self.admin,
            user=user,
        )
        assert NetworkRule.objects.count() == 2

    def test_destroy_success(self):
        """Tests that you can successfully delete a NetworkRule instance"""
        assert NetworkRule.objects.count() == 2
        response = self.client.delete(self.first_rule_url)
        assert response.status_code == self.valid_status_code
        assert NetworkRule.objects.count() == 1
        response = self.client.delete(self.second_rule_url)
        assert response.status_code == self.valid_status_code
        assert NetworkRule.objects.count() == 0
