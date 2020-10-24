"""TestCase for the 'retrieve' action"""


# Django
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
class TestRetrieveIp(ActionTestCase):
    """TestCase for the 'retrieve' action"""

    service_base_url = f"{SERVICE_URL}/"

    # ----------------------------------------
    # Behavior
    # ----------------------------------------
    @classmethod
    def setUpClass(cls):
        """Sets up the API client"""
        cls.client = APIClient()

    def setUp(self):
        """Creates and authenticates an Admin user, and creates 2 IpAddress instances"""
        self.admin = self.create_admin_user(authenticate=True)
        self.first_ip = create_ip_address()
        self.second_ip = create_ip_address(ip="127.0.0.2")
        self.first_ip_url = self.detail_url(self.first_ip.id)
        self.second_ip_url = self.detail_url(self.second_ip.id)

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
        response = self.client.get(self.first_ip_url)
        assert response.status_code == 401
        # 403 Not admin
        self.create_user(authenticate=True)
        response = self.client.get(self.first_ip_url)
        assert response.status_code == 403
        # 201 Admin
        self.client.logout()
        self.client.force_authenticate(self.admin)
        response = self.client.get(self.first_ip_url)
        assert response.status_code == 200

    def test_unknown_ip_address(self):
        """Tests that we cannot fetch an unknown IP"""
        unknown_url = self.detail_url(10)
        # Admin should get 404
        assert IpAddress.objects.count() == 2
        response = self.client.get(unknown_url)
        assert response.status_code == 404
        # User should get 403
        self.client.logout()
        self.create_user(authenticate=True)
        response = self.client.get(unknown_url)
        assert response.status_code == 403

    def test_retrieve_success(self):
        """Tests that we can successfully retrieve an IP"""
        for instance, url in [
            (self.first_ip, self.first_ip_url),
            (self.second_ip, self.second_ip_url),
        ]:
            response = self.client.get(url)
            assert response.status_code == 200
            assert_representation_matches_instance(response.data, instance)
