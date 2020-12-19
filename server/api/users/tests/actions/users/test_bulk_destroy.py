"""TestCase for the 'bulk_destroy' action"""


# Django
from django.contrib.auth.models import User
from rest_framework.test import APIClient

# Personal
from jklib.django.db.queries import get_object_or_none
from jklib.django.drf.tests import ActionTestCase

# Local
from ._shared import USER_SERVICE_URL


# --------------------------------------------------------------------------------
# > TestCase
# --------------------------------------------------------------------------------
class TestDestroyManyUsers(ActionTestCase):
    """TestCase for the 'bulk_destroy' action"""

    service_base_url = f"{USER_SERVICE_URL}/bulk_destroy/"
    success_code = 204

    # ----------------------------------------
    # Behavior
    # ----------------------------------------
    @classmethod
    def setUpClass(cls):
        """Sets up the API client"""
        cls.client = APIClient()

    def setUp(self):
        """Creates 1 admin, a valid payload, and 9 other User instances"""
        self.admin = self.create_admin_user()
        self.payload = {"ids": [3, 4]}
        for i in range(9):
            self.create_user()

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
        """Tests only admins can use this service"""
        # 401 Not authenticated
        response = self.client.delete(self.service_base_url, data=self.payload)
        assert response.status_code == 401
        assert User.objects.count() == 10
        # 403 user
        user = self.create_user()
        self.client.force_authenticate(user)
        response = self.client.delete(self.service_base_url, data=self.payload)
        assert response.status_code == 403
        assert User.objects.count() == 11
        # 204 Admin
        self.client.logout()
        self.client.force_authenticate(self.admin)
        response = self.client.delete(self.service_base_url, data=self.payload)
        assert response.status_code == 204
        assert User.objects.count() == 9

    def test_ids(self):
        """Tests that you must provide a list of integers"""
        self.client.force_authenticate(self.admin)
        invalid_values = [None, "test", 10, ["string", 33]]
        for value in invalid_values:
            self.payload["ids"] = value
            response = self.client.delete(self.service_base_url, data=self.payload)
            self.assert_field_has_error(response, "ids")
        assert User.objects.count() == 10

    def test_no_valid_ids(self):
        """Tests that you get a 404 if no instance is found with your ids"""
        self.client.force_authenticate(self.admin)
        self.payload["ids"] = [11, 12, 13]
        response = self.client.delete(self.service_base_url, data=self.payload)
        assert response.status_code == 404
        assert User.objects.count() == 10

    def test_only_valid_ids(self):
        """Tests that valid IDs are successfully deleted"""
        self.client.force_authenticate(self.admin)
        ids_to_delete = [2, 4, 7]
        self.payload["ids"] = ids_to_delete
        response = self.client.delete(self.service_base_url, data=self.payload)
        assert response.status_code == 204
        assert User.objects.count() == 7
        for id_ in ids_to_delete:
            assert get_object_or_none(User, pk=id_) is None

    def test_some_valid_ids(self):
        """Tests that only valid IDs get successfully deleted"""
        self.client.force_authenticate(self.admin)
        ids_to_delete = [2, 4, 18]
        self.payload["ids"] = ids_to_delete
        response = self.client.delete(self.service_base_url, data=self.payload)
        assert response.status_code == 204
        assert User.objects.count() == 8
        for id_ in ids_to_delete:
            assert get_object_or_none(User, pk=id_) is None
