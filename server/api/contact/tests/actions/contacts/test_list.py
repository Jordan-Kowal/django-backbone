"""TestCase for the 'list' action"""


# Django
from rest_framework.test import APIClient

# Personal
from jklib.django.drf.tests import ActionTestCase

# Local
from ....models import Contact
from ._shared import BASE_URL, assert_response_matches_instance, create_contact


# --------------------------------------------------------------------------------
# > TestCase
# --------------------------------------------------------------------------------
class TestDestroyContact(ActionTestCase):
    """TestCase for the 'create' action"""

    service_base_url = f"{BASE_URL}/"
    success_code = 200

    # ----------------------------------------
    # Behavior
    # ----------------------------------------
    @classmethod
    def setUpClass(cls):
        """Sets up the API client"""
        cls.client = APIClient()

    def setUp(self):
        """Creates 1 admin and 1 user"""
        self.user = self.create_user()
        self.admin = self.create_admin_user()

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
        """Tests that only admins can access this service"""
        # 401 not authenticated
        response = self.client.get(self.service_base_url)
        assert response.status_code == 401
        # 403 not admin
        self.client.force_authenticate(self.user)
        response = self.client.get(self.service_base_url)
        assert response.status_code == 403
        # 204 admin
        self.client.logout()
        self.client.force_authenticate(self.admin)
        response = self.client.get(self.service_base_url)
        assert response.status_code == self.success_code

    def test_success_zero(self):
        """Tests the service works even if no instance is found"""
        self.client.force_authenticate(self.admin)
        assert Contact.objects.count() == 0
        response = self.client.get(self.service_base_url)
        assert response.status_code == self.success_code
        assert len(response.data) == 0

    def test_success_one(self):
        """Tests the service works with 1 entry in the database"""
        self.client.force_authenticate(self.admin)
        instance = create_contact(subject="Subject 1")
        response = self.client.get(self.service_base_url)
        assert response.status_code == self.success_code
        assert len(response.data) == 1
        assert_response_matches_instance(response.data[0], instance)

    def test_success_many(self):
        """Tests all instances a returned correctly"""
        self.client.force_authenticate(self.admin)
        instance_1 = create_contact(subject="Subject 1")
        instance_2 = create_contact(subject="Subject 2", user=self.user)
        response = self.client.get(self.service_base_url)
        assert response.status_code == self.success_code
        assert len(response.data) == 2
        assert_response_matches_instance(response.data[1], instance_1)
        assert_response_matches_instance(response.data[0], instance_2)
