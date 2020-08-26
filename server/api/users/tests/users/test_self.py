"""TestCase for the 'self' actions"""


# Django
from django.contrib.auth.models import User
from rest_framework.test import APIClient

# Personal
from jklib.django.drf.tests import ActionTestCase

# Local
from ._shared import USER_SERVICE_URL, assert_user_representation_matches_instance


# --------------------------------------------------------------------------------
# > TestCase
# --------------------------------------------------------------------------------
class TestSelfActions(ActionTestCase):
    """
    Tests the 'self' service that is comprised of 3 actions:
        GET to fetch the user data
        PUT to update the user data
        DELETE to delete the user
    It is similar to the "model" action, except that the targeted user is the one performing the request
    """

    service_url = f"{USER_SERVICE_URL}/self/"
    required_fields = ["email"]

    # ----------------------------------------
    # Behavior
    # ----------------------------------------
    @classmethod
    def setUpClass(cls):
        """Sets up the API client"""
        cls.client = APIClient()

    def setUp(self):
        """Creates 2 basic users"""
        self.user = self.create_user()
        self.other_user = self.create_user()

    def teardown(self):
        """Removes all users from the database and logs out the current client"""
        User.objects.all().delete()
        self.client.logout()

    @classmethod
    def tearDownClass(cls):
        """Not implemented"""
        pass

    # ----------------------------------------
    # Tests for retrieve (GET)
    # ----------------------------------------
    def test_retrieve_permissions(self):
        """Tests that you must be authenticated to call this service"""
        # 401 Unauthorized
        response = self.client.get(self.service_url)
        assert response.status_code == 401
        # 200 Ok
        self.client.force_authenticate(self.user)
        response = self.client.get(self.service_url)
        assert response.status_code == 200

    def test_retrieve_success(self):
        """Tests that we correctly fetch the current user"""
        for user in (self.user, self.other_user):
            self.client.force_authenticate(user)
            response = self.client.get(self.service_url)
            assert response.status_code == 200
            assert_user_representation_matches_instance(response.data, user)
            self.client.logout()

    # ----------------------------------------
    # Tests for update (PUT)
    # ----------------------------------------
    def test_update_permissions(self):
        """Tests that you must be authenticated to call this service"""
        self.update_setup(auth=False)
        # 401 Unauthorized
        response = self.client.put(self.service_url, self.payload)
        assert response.status_code == 401
        # 200 Ok
        self.client.force_authenticate(self.user)
        response = self.client.put(self.service_url, self.payload)
        assert response.status_code == 200

    def test_update_required_fields(self):
        """Tests that 'email' is a required field"""
        self.update_setup()
        self.assert_fields_are_required(self.client.put, self.service_url, self.payload)

    def test_update_email_format(self):
        """Tests that 'email' must be a valid email format"""
        self.update_setup()
        # Invalid Email 1
        self.payload["email"] = "invalid@email"
        response = self.client.put(self.service_url, self.payload)
        self.assert_field_has_error(response, "email")
        # Invalid Email 2
        self.payload["email"] = 33
        response = self.client.put(self.service_url, self.payload)
        self.assert_field_has_error(response, "email")

    def test_update_unique_email(self):
        """Tests that you can't use an already taken email"""
        self.update_setup()
        # Try to update with an already-taken email
        self.payload["email"] = self.other_user.email
        response = self.client.put(self.service_url, self.payload)
        self.assert_field_has_error(response, "email")
        # We make sure his email hasn't changed
        our_user = User.objects.get(id=self.user.id)
        assert our_user.email == self.user.email != self.other_user.email

    def test_update_success(self):
        """Tests that you can successfully update your user info"""
        self.update_setup()
        response = self.client.put(self.service_url, self.payload)
        data = response.data
        user = User.objects.get(id=self.user.id)
        assert response.status_code == 200
        # User has been updated
        assert user.email == data["email"] == self.payload["email"]
        assert user.first_name == data["first_name"] == self.payload["first_name"]
        assert user.last_name == data["last_name"] == self.payload["last_name"]
        assert user.email == user.username

    def test_update_cannot_update_other_fields(self):
        """Tests that the 'is_active' field cannot be updated through this service"""
        self.update_setup()
        self.payload["is_active"] = not self.user.is_active
        response = self.client.put(self.service_url, self.payload)
        updated_user = User.objects.get(id=self.user.id)
        assert response.status_code == 200
        assert self.user.is_active == updated_user.is_active  # No change

    # ----------------------------------------
    # Tests for destroy (DELETE)
    # ----------------------------------------
    def test_destroy_permissions(self):
        """Tests that you must be authenticated to call this service"""
        # 401 Unauthorized
        response = self.client.delete(self.service_url)
        assert response.status_code == 401
        # 200 Ok
        self.client.force_authenticate(self.user)
        response = self.client.delete(self.service_url)
        assert response.status_code == 204

    def test_destroy_success(self):
        """Tests that we correctly delete the current user"""
        # Deletes the user
        self.client.force_authenticate(self.user)
        response = self.client.delete(self.service_url)
        assert response.status_code == 204
        assert User.objects.count() == 1
        # Doing it again should not work
        # Returns 403 instead of 401 because still "logged in" but user has no ID (because deleted)
        response = self.client.delete(self.service_url)
        assert response.status_code == 403

    # ----------------------------------------
    # Utilities
    # ----------------------------------------
    def update_setup(self, auth=True):
        """Sets a valid payload for update and potentially authenticates the user 'self.user'"""
        data = self.generate_random_user_data()
        self.payload = {
            "email": data["email"],
            "first_name": data["username"],
            "last_name": data["last_name"],
        }
        if auth:
            self.client.force_authenticate(self.user)
