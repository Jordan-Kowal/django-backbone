"""TestCase for the 'destroy' action"""


# Django
from rest_framework.test import APIClient

# Personal
from jklib.django.drf.tests import ActionTestCase

# Local
from ....models import Contact
from ._shared import BASE_URL


# --------------------------------------------------------------------------------
# > TestCase
# --------------------------------------------------------------------------------
class TestDestroyContact(ActionTestCase):
    """TestCase for the 'create' action"""

    service_base_url = f"{BASE_URL}/"
    success_code = 204

    # ----------------------------------------
    # Behavior
    # ----------------------------------------
    @classmethod
    def setUpClass(cls):
        """Sets up the API client"""
        cls.client = APIClient()

    def setUp(self):
        """Creates 1 admin, 1 user, and 2 contact"""
        self.user = self.create_user()
        self.admin = self.create_admin_user()
        payload = {
            "ip": "123.0.0.4",
            "name": "Contact name",
            "email": "fake.email.for.test@domain.test",
            "subject": "Subject for the contact request",
            "body": "Content of the contact request, aka the body",
        }
        self.contact_1 = Contact.objects.create(**payload)
        self.contact_1_url = self.detail_url(self.contact_1.id)
        self.contact_2 = Contact.objects.create(**payload)
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
        response = self.client.delete(self.contact_1_url)
        assert response.status_code == 401
        assert Contact.objects.count() == 2
        # 403 not admin
        self.client.force_authenticate(self.user)
        response = self.client.delete(self.contact_1_url)
        assert response.status_code == 403
        assert Contact.objects.count() == 2
        # 204 admin
        self.client.logout()
        self.client.force_authenticate(self.admin)
        response = self.client.delete(self.contact_1_url)
        assert response.status_code == 204
        assert Contact.objects.count() == 1

    def test_unknown_instance(self):
        """Tests that you get a 404 if you target an unknown ID"""
        self.client.force_authenticate(self.admin)
        invalid_url = self.detail_url(10)
        response = self.client.delete(invalid_url)
        assert response.status_code == 404
        assert Contact.objects.count() == 2

    def test_success(self):
        """Tests that you can successfully delete Contact instances"""
        self.client.force_authenticate(self.admin)
        # Delete id 1
        response = self.client.delete(self.contact_1_url)
        assert response.status_code == self.success_code
        assert Contact.objects.count() == 1
        # Delete id 2
        response = self.client.delete(self.contact_2_url)
        assert response.status_code == self.success_code
        assert Contact.objects.count() == 0
        # Deleting id 2 again should return 404
        response = self.client.delete(self.contact_2_url)
        assert response.status_code == 404
