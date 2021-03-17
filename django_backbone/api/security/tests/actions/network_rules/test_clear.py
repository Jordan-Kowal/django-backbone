"""TestCase for the 'clear' action"""

# Personal
from jklib.django.drf.tests import ActionTestCase
from jklib.django.utils.tests import assert_logs

# Local
from ....models import NetworkRule
from ._shared import (
    SERVICE_URL,
    assert_admin_permissions,
    assert_representation_matches_instance,
    assert_unknown_instance,
    create_network_rule,
)


# --------------------------------------------------------------------------------
# > TestCase
# --------------------------------------------------------------------------------
class TestClearNetworkRule(ActionTestCase):
    """TestCase for the 'clear' action"""

    service_base_url = f"{SERVICE_URL}/"
    service_extra_url = "clear/"
    valid_status_code = 200

    # ----------------------------------------
    # Behavior
    # ----------------------------------------
    @assert_logs("security", "INFO")
    def setUp(self):
        """Creates and authenticates an Admin user, and creates 1 NetworkRule instance"""
        self.admin = self.create_admin_user(authenticate=True)
        self.rule = create_network_rule()
        self.rule_url = self.detail_url(self.rule.id)

    # ----------------------------------------
    # Tests
    # ----------------------------------------
    @assert_logs("security", "INFO")
    def test_permissions(self):
        """Tests that only admin users can access this service"""
        user = self.create_user()
        assert_admin_permissions(
            client=self.client,
            protocol=self.client.post,
            url=self.rule_url,
            payload=None,
            valid_status_code=self.valid_status_code,
            admin=self.admin,
            user=user,
        )

    def test_unknown_instance(self):
        """Tests that you can clear an unknown NetworkRule"""
        unknown_url = self.detail_url(10)
        user = self.create_user()
        assert_unknown_instance(
            client=self.client,
            protocol=self.client.post,
            url=unknown_url,
            payload=None,
            admin=self.admin,
            user=user,
        )

    @assert_logs("security", "INFO")
    def test_clear_success_with_change(self):
        """Tests that you can clear a blacklisted NetworkRule"""
        # Perform the request on blacklisted rule
        self.rule.blacklist()
        response = self.client.post(self.rule_url)
        # Check the rule has been updated
        assert response.status_code == self.valid_status_code
        updated_instance = NetworkRule.objects.get(pk=self.rule.id)
        was_updated = response.data.pop("updated")
        assert was_updated
        assert_representation_matches_instance(response.data, updated_instance)

    @assert_logs("security", "INFO")
    def test_clear_success_without_change(self):
        """Tests that clearing an already-cleared rule doesn't do anything"""
        # Perform the request on a cleared rule
        self.rule.clear()
        response = self.client.post(self.rule_url)
        # Check nothing changed
        assert response.status_code == self.valid_status_code
        updated_instance = NetworkRule.objects.get(pk=self.rule.id)
        was_updated = response.data.pop("updated")
        assert not was_updated
        assert_representation_matches_instance(response.data, updated_instance)
