"""TestCase for the 'update' service"""

# Django
from django.contrib.auth.models import User
from rest_framework.test import APIClient

# Personal
from jklib.django.drf.tests import ActionTestCase

# Local
from ._shared import USER_SERVICE_URL


# --------------------------------------------------------------------------------
# > TestCase
# --------------------------------------------------------------------------------
class TestUpdateUser(ActionTestCase):
    """TestCase for the 'update' service"""

    service_url = f"{USER_SERVICE_URL}/"
    required_fields = ["email"]

    # ----------------------------------------
    # Behavior
    # ----------------------------------------
    @classmethod
    def setUpClass(cls):
        """Sets up the API client"""
        cls.client = APIClient()

    def setUp(self):
        """Creates 2 user (1 admin and 1 normal) and generates a valid payload"""
        self.generate_users()
        self.generate_payload()
        assert User.objects.count() == 2

    def teardown(self):
        """Removes all users from the database and logs out the current client"""
        User.objects.all().delete()
        self.client.logout()

    @classmethod
    def tearDownClass(cls):
        """Not implemented"""
        pass

    # ----------------------------------------
    # Tests
    # ----------------------------------------
    def test_permissions(self):
        """Tests that access is restricted to owner or admins"""
        # 401 Unauthenticated
        response = self.client.put(self.admin_detail_url, self.payload)
        assert response.status_code == 401
        # 403 Not owner
        self.client.force_authenticate(self.user)
        response = self.client.put(self.admin_detail_url, self.payload)
        assert response.status_code == 403
        # 200 Owner
        response = self.client.put(self.user_detail_url, self.payload)
        assert response.status_code == 200
        # 200 Admin
        self.client.logout()
        self.client.force_authenticate(self.admin)
        response = self.client.put(self.user_detail_url, self.payload)
        assert response.status_code == 200

    def test_unknown_user(self):
        """Tests that we cannot update an unknown user"""
        invalid_url = self.detail_url(3)
        # Admin can't find it
        self.client.force_authenticate(self.admin)
        response = self.client.put(invalid_url, self.payload)
        assert response.status_code == 404
        # User can't find it
        self.client.logout()
        self.client.force_authenticate(self.user)
        response = self.client.put(invalid_url, self.payload)
        assert response.status_code == 404

    def test_required_fields(self):
        """Tests that the required fields truly are required"""
        self.client.force_authenticate(self.user)
        self.assert_fields_are_required(
            self.client.put, self.user_detail_url, self.payload
        )

    def test_email_format(self):
        """Tests that the email field must be an actual email"""
        self.client.force_authenticate(self.user)
        # Almost an email
        self.payload["email"] = "invalid@email"
        response = self.client.put(self.user_detail_url, data=self.payload)
        self.assert_field_has_error(response, "email")
        # Totally not an email
        self.payload["email"] = 33
        response = self.client.put(self.user_detail_url, data=self.payload)
        self.assert_field_has_error(response, "email")

    def test_unique_email(self):
        """Tests that we cannot change the email to an existing one"""
        self.client.force_authenticate(self.user)
        self.payload["email"] = self.admin.email
        response = self.client.put(self.user_detail_url, self.payload)
        updated_user = User.objects.get(id=self.user.id)
        self.assert_field_has_error(response, "email")
        assert updated_user.email == self.user.email != self.admin.email

    def test_update_success(self):
        """
        Tests that we successfully updated our user
        After the update, "self.user" holds the previous version/data of our user
        So we can compare it to the updated object to see if a change has been made
        """
        # Performing the update
        self.client.force_authenticate(self.user)
        response = self.client.put(self.user_detail_url, data=self.payload)
        user = User.objects.get(id=self.user.id)
        data = response.data
        assert response.status_code == 200
        # User has been updated
        assert user.email == data["email"] == self.payload["email"]
        assert user.first_name == data["first_name"] == self.payload["first_name"]
        assert user.last_name == data["last_name"] == self.payload["last_name"]
        assert user.email == user.username

    def test_cannot_update_other_fields(self):
        """Tests that we cannot update another field like 'is_active'"""
        self.payload["is_active"] = not self.user.is_active
        self.client.force_authenticate(self.user)
        response = self.client.put(self.user_detail_url, self.payload)
        updated_user = User.objects.get(id=self.user.id)
        assert response.status_code == 200
        assert updated_user.is_active == self.user.is_active  # No change

    # ----------------------------------------
    # Private
    # ----------------------------------------
    def generate_payload(self):
        """Generates a valid payload for the service with unique data and stores it in self.payload"""
        data = self.generate_random_user_data()
        self.payload = {
            "email": data["email"],
            "first_name": data["username"],
            "last_name": data["last_name"],
        }

    def generate_users(self):
        """Creates 1 admin and 1 user and also stores their detail URL for the service"""
        self.admin = self.create_admin_user()
        self.admin_detail_url = self.detail_url(self.admin.id)
        self.user = self.create_user()
        self.user_detail_url = self.detail_url(self.user.id)
