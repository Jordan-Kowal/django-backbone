"""TestCase for the 'destroy' action"""


# Django
from rest_framework.test import APIClient

# Personal
from jklib.django.drf.tests import ActionTestCase

# Local
from ....models import IpAddress
from ._shared import (
    SERVICE_URL,
    assert_admin_permissions,
    assert_unknown_ip,
    create_ip_address,
)


# --------------------------------------------------------------------------------
# > TestCase
# --------------------------------------------------------------------------------
class TestDestroyUser(ActionTestCase):
    """TestCase for the 'destroy' action"""

    service_base_url = f"{SERVICE_URL}/"
    valid_status_code = 204

    # ----------------------------------------
    # Behavior
    # ----------------------------------------
    @classmethod
    def setUpClass(cls):
        """Sets up the API client"""
        cls.client = APIClient()

    def setUp(self):
        """Creates and authenticates an admin user and creates 2 IpAddress instances"""
        self.admin = self.create_admin_user(authenticate=True)
        self.first_ip = create_ip_address()
        self.first_ip_url = self.detail_url(self.first_ip.id)
        self.second_ip = create_ip_address(ip="127.0.0.2")
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
        """Tests that only admin users can use this service"""
        user = self.create_user()
        assert_admin_permissions(
            client=self.client,
            protocol=self.client.delete,
            url=self.first_ip_url,
            payload=None,
            valid_status_code=self.valid_status_code,
            admin=self.admin,
            user=user,
        )
        assert IpAddress.objects.count() == 1

    def test_unknown_ip_address(self):
        """Tests that you get an error when trying to delete an unknown object"""
        unknown_url = self.detail_url(10)
        user = self.create_user()
        assert_unknown_ip(
            client=self.client,
            protocol=self.client.delete,
            url=unknown_url,
            payload=None,
            admin=self.admin,
            user=user,
        )
        assert IpAddress.objects.count() == 2

    def test_destroy_success(self):
        """Tests that you can successfully delete an IP"""
        assert IpAddress.objects.count() == 2
        response = self.client.delete(self.first_ip_url)
        assert response.status_code == self.valid_status_code
        assert IpAddress.objects.count() == 1
        response = self.client.delete(self.second_ip_url)
        assert response.status_code == self.valid_status_code
        assert IpAddress.objects.count() == 0
