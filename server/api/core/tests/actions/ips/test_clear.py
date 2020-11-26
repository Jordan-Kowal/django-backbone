"""TestCase for the 'clear' action"""


# Django
from rest_framework.test import APIClient

# Personal
from jklib.django.drf.tests import ActionTestCase

# Local
from ....models import IpAddress
from ._shared import (
    SERVICE_URL,
    assert_admin_permissions,
    assert_representation_matches_instance,
    assert_unknown_ip,
    create_ip_address,
)


# --------------------------------------------------------------------------------
# > TestCase
# --------------------------------------------------------------------------------
class TestClearIp(ActionTestCase):
    """TestCase for the 'clear' action"""

    service_base_url = f"{SERVICE_URL}/"
    service_extra_url = "clear/"
    valid_status_code = 200

    # ----------------------------------------
    # Behavior
    # ----------------------------------------
    @classmethod
    def setUpClass(cls):
        """Sets up the API client"""
        cls.client = APIClient()

    def setUp(self):
        """Creates and authenticates an Admin user, and creates 1 IpAddress instance"""
        self.admin = self.create_admin_user(authenticate=True)
        self.ip = create_ip_address()
        self.ip_url = self.detail_url(self.ip.id)

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
            client=self.client,
            protocol=self.client.post,
            url=self.ip_url,
            payload=None,
            valid_status_code=self.valid_status_code,
            admin=self.admin,
            user=user,
        )

    def test_unknown_ip(self):
        """Tests that you can clear an unknown IP"""
        unknown_url = self.detail_url(10)
        user = self.create_user()
        assert_unknown_ip(
            client=self.client,
            protocol=self.client.post,
            url=unknown_url,
            payload=None,
            admin=self.admin,
            user=user,
        )

    def test_clear_success_with_change(self):
        """Tests that you can clear a blacklisted IP"""
        # Perform the request on blacklisted IP
        self.ip.blacklist()
        response = self.client.post(self.ip_url)
        # Check the IP has been updated
        assert response.status_code == self.valid_status_code
        updated_ip = IpAddress.objects.get(pk=self.ip.id)
        was_updated = response.data.pop("updated")
        assert was_updated
        assert_representation_matches_instance(response.data, updated_ip)

    def test_clear_success_without_change(self):
        """Tests that clearing an already-cleared IP doesn't do anything"""
        # Perform the request on a cleared IP
        self.ip.clear()
        response = self.client.post(self.ip_url)
        # Check nothing changed
        assert response.status_code == self.valid_status_code
        updated_ip = IpAddress.objects.get(pk=self.ip.id)
        was_updated = response.data.pop("updated")
        assert not was_updated
        assert_representation_matches_instance(response.data, updated_ip)
