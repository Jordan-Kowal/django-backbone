"""TestCase for the 'retrieve' action"""


# Django
from rest_framework.test import APIClient

# Personal
from jklib.django.drf.tests import ActionTestCase

# Local
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
class TestRetrieveNetworkRule(ActionTestCase):
    """TestCase for the 'retrieve' action"""

    service_base_url = f"{SERVICE_URL}/"
    valid_status_code = 200

    # ----------------------------------------
    # Behavior
    # ----------------------------------------
    @classmethod
    def setUpClass(cls):
        """Sets up the API client"""
        cls.client = APIClient()

    def setUp(self):
        """Creates and authenticates an Admin user, and creates 2 NetworkRule instances"""
        self.admin = self.create_admin_user(authenticate=True)
        self.first_rule = create_network_rule()
        self.second_rule = create_network_rule(ip="127.0.0.2")
        self.first_rule_url = self.detail_url(self.first_rule.id)
        self.second_rule_url = self.detail_url(self.second_rule.id)

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
        """Tests that only admin user can retrieve a NetworkRule instance"""
        user = self.create_user()
        assert_admin_permissions(
            client=self.client,
            protocol=self.client.get,
            url=self.first_rule_url,
            payload=None,
            valid_status_code=self.valid_status_code,
            admin=self.admin,
            user=user,
        )

    def test_unknown_instance(self):
        """Tests that we cannot fetch an unknown instance"""
        unknown_url = self.detail_url(10)
        user = self.create_user()
        assert_unknown_instance(
            client=self.client,
            protocol=self.client.get,
            url=unknown_url,
            payload=None,
            admin=self.admin,
            user=user,
        )

    def test_retrieve_success(self):
        """Tests that we can successfully retrieve an NetworkRule instance"""
        for instance, url in [
            (self.first_rule, self.first_rule_url),
            (self.second_rule, self.second_rule_url),
        ]:
            response = self.client.get(url)
            assert response.status_code == self.valid_status_code
            assert_representation_matches_instance(response.data, instance)
