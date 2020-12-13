"""TestCase for the 'destroy' action"""


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
        """Creates 1 admin, 1 user, and 2 Contact instances"""
        self.user = self.create_user()
        self.admin = self.create_admin_user()
        self.contact_1 = create_contact(subject="Subject 1")
        self.contact_1_url = self.detail_url(self.contact_1.id)
        self.contact_2 = create_contact(subject="Subject 2", user=self.user)
        self.contact_2_url = self.detail_url(self.contact_2.id)

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
        response = self.client.get(self.contact_1_url)
        assert response.status_code == 401
        assert Contact.objects.count() == 2
        # 403 not admin
        self.client.force_authenticate(self.user)
        response = self.client.get(self.contact_1_url)
        assert response.status_code == 403
        assert Contact.objects.count() == 2
        # 204 admin
        self.client.logout()
        self.client.force_authenticate(self.admin)
        response = self.client.get(self.contact_1_url)
        assert response.status_code == self.success_code
        assert Contact.objects.count() == 2

    def test_unknown_instance(self):
        """Tests that you get a 404 if you target an unknown ID"""
        self.client.force_authenticate(self.admin)
        invalid_url = self.detail_url(10)
        response = self.client.get(invalid_url)
        assert response.status_code == 404
        assert Contact.objects.count() == 2

    def test_success(self):
        """Tests that you can correctly fetch a Contact instance"""
        self.client.force_authenticate(self.admin)
        for instance, url in [
            (self.contact_1, self.contact_1_url),
            (self.contact_2, self.contact_2_url),
        ]:
            response = self.client.get(url)
            assert response.status_code == self.success_code
            assert_response_matches_instance(response.data, instance)
