"""TestCase for the 'blacklist_existing' action"""

# Personal
from jklib.django.drf.tests import ActionTestCase

# Local
from ....models import NetworkRule
from ._shared import (
    SERVICE_URL,
    assert_admin_permissions,
    assert_comment_length,
    assert_expires_on_is_optional,
    assert_override_condition,
    assert_representation_matches_instance,
    assert_unknown_instance,
    assert_valid_expires_on,
    create_network_rule,
)


# --------------------------------------------------------------------------------
# > TestCase
# --------------------------------------------------------------------------------
class TestBlacklistNetworkRule(ActionTestCase):
    """TestCase for the 'blacklist_existing' action"""

    service_base_url = f"{SERVICE_URL}/"
    service_extra_url = "blacklist/"
    valid_status_code = 200

    # ----------------------------------------
    # Behavior
    # ----------------------------------------
    def setUp(self):
        """Creates and authenticates an Admin user, and creates 1 NetworkRule instance and a payload"""
        self.admin = self.create_admin_user(authenticate=True)
        self.rule = create_network_rule()
        self.rule_url = self.detail_url(self.rule.id)
        self.default_payload = {
            "expires_on": None,
            "comment": "Test comment",
            "override": False,
        }

    # ----------------------------------------
    # Tests
    # ----------------------------------------
    def test_permissions(self):
        """Tests that only admin user can use this service"""
        user = self.create_user()
        assert_admin_permissions(
            client=self.client,
            protocol=self.client.post,
            url=self.rule_url,
            payload=self.default_payload,
            valid_status_code=self.valid_status_code,
            admin=self.admin,
            user=user,
        )

    def test_unknown_instance(self):
        """Tests that we cannot blacklist an unknown instance"""
        unknown_url = self.detail_url(10)
        user = self.create_user()
        assert_unknown_instance(
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
            url=self.rule_url,
            payload=self.default_payload,
            valid_status_code=self.valid_status_code,
        )

    def test_expires_on_optional(self):
        """Tests that the 'expires_on' gets defaulted if not provided"""
        assert_expires_on_is_optional(
            protocol=self.client.post,
            url=self.rule_url,
            payload=self.default_payload,
            valid_status_code=self.valid_status_code,
            id_=self.rule.id,
        )

    def test_valid_expires_on(self):
        """Tests that you must provide a valid date in format and value"""
        assert_valid_expires_on(
            protocol=self.client.post,
            url=self.rule_url,
            payload=self.default_payload,
            valid_status_code=self.valid_status_code,
            clean_up=False,
        )

    def test_override_check(self):
        """Tests that a whitelisted instance can be blacklisted only with 'override=True'"""
        second_rule = create_network_rule(ip="127.0.0.2")
        second_rule_url = self.detail_url(second_rule.id)
        second_rule.whitelist()
        assert_override_condition(
            protocol=self.client.post,
            url=second_rule_url,
            payload=self.default_payload,
            valid_status_code=self.valid_status_code,
            id_=second_rule.id,
            status=NetworkRule.Status.BLACKLISTED,
        )

    def test_blacklist_success(self):
        """Tests that we can successfully blacklist an existing rule"""
        assert not self.rule.is_blacklisted
        response = self.client.post(self.rule_url)
        assert response.status_code == self.valid_status_code
        updated_instance = NetworkRule.objects.get(pk=self.rule.id)
        assert updated_instance.is_blacklisted
        assert_representation_matches_instance(response.data, updated_instance)
