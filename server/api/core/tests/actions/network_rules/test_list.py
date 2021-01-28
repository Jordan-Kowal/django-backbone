"""TestCase for the 'list' action"""

# Django
from rest_framework.test import APIClient

# Personal
from jklib.django.drf.tests import ActionTestCase

# Local
from ....models import NetworkRule
from ._shared import (
    SERVICE_URL,
    assert_admin_permissions,
    assert_representation_matches_instance,
    create_network_rule,
)


# --------------------------------------------------------------------------------
# > TestCase
# --------------------------------------------------------------------------------
class TestListNetworkRules(ActionTestCase):
    """TestCase for the 'list' action"""

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
        """Creates and authenticates an Admin user"""
        self.admin = self.create_admin_user(authenticate=True)

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
        """Tests that only admin can access this service"""
        create_network_rule()
        assert NetworkRule.objects.count() == 1
        user = self.create_user()
        assert_admin_permissions(
            client=self.client,
            protocol=self.client.get,
            url=self.service_base_url,
            payload=None,
            valid_status_code=self.valid_status_code,
            admin=self.admin,
            user=user,
        )

    def test_list_zero(self):
        """Tests that the service works even if there's no object"""
        assert NetworkRule.objects.count() == 0
        response = self.client.get(self.service_base_url)
        assert response.status_code == self.valid_status_code
        assert len(response.data) == 0

    def test_list_one(self):
        """Tests that the service works even if there's only 1 object"""
        first_rule = create_network_rule()
        assert NetworkRule.objects.count() == 1
        response = self.client.get(self.service_base_url)
        assert response.status_code == self.valid_status_code
        assert len(response.data) == 1
        assert_representation_matches_instance(response.data[0], first_rule)

    def test_list_many(self):
        """Tests that the service returns all IPs correctly"""
        # Create the instances
        first_rule = create_network_rule()
        second_rule = create_network_rule(ip="127.0.0.2")
        third_rule = create_network_rule(ip="127.0.0.3")
        assert NetworkRule.objects.count() == 3
        # Perform the request
        response = self.client.get(self.service_base_url)
        assert response.status_code == self.valid_status_code
        assert len(response.data) == 3
        # Check all instances
        instances = [first_rule, second_rule, third_rule]
        count = len(instances)
        for i, instance in enumerate(instances):
            matching_index = count - i - 1
            assert_representation_matches_instance(
                response.data[matching_index], instance
            )
