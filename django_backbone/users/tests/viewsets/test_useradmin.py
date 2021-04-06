"""Tests for the User-related viewsets"""

# Personal
from jklib.django.drf.tests import ActionTestCase

# Application
# --------------------------------------------------------------------------------
# > Helpers
# --------------------------------------------------------------------------------
from users.models import User

SERVICE_URL = "/api/admin/users/"


class Base(ActionTestCase):
    """Base class for testing the UserAdmin API"""

    def setUp(self):
        """Creates and authenticates an admin user"""
        self.admin = self.create_admin_user(authenticate=True)

    def assert_password_strength(self):
        """Checks the password strength"""
        self.payload["password"] = "test"
        self.payload["confirm_password"] = "test"
        response = self.http_method(self.url(), data=self.payload)
        assert response.status_code == 400
        assert len(response.data["password"]) > 0

    def assert_matching_password(self):
        """Checks both passwords must match"""
        self.payload["password"] = "Str0ngEn0ugh"
        self.payload["confirm_password"] = "test"
        response = self.http_method(self.url(), data=self.payload)
        assert response.status_code == 400
        assert len(response.data["confirm_password"]) > 0

    @staticmethod
    def assert_response_matches_objects(response_data, instance=None, payload=None):
        """
        Checks if the response matches an instance and/or a payload
        :param dict response_data: The response data
        :param User instance: The matching user instance
        :param dict payload: The payload used in the request
        """
        assert "password" not in response_data
        assert "confirm_password" not in response_data
        if instance is not None:
            assert response_data["email"] == instance.email
            assert response_data["first_name"] == instance.first_name
            assert response_data["last_name"] == instance.last_name
            assert response_data["is_active"] == instance.is_active
            assert response_data["is_staff"] == instance.is_staff
            assert response_data["is_verified"] == instance.is_verified
        if payload is not None:
            assert response_data["email"] == payload.get("email")
            assert response_data["first_name"] == payload.get("first_name", "")
            assert response_data["last_name"] == payload.get("last_name", "")
            assert response_data["is_active"] == payload.get("is_active", True)
            assert response_data["is_staff"] == payload.get("is_staff", False)
            assert response_data["is_verified"] == payload.get("is_verified", False)


# --------------------------------------------------------------------------------
# > TestCases
# --------------------------------------------------------------------------------
class TestAdminCreateUser(Base):
    """TestCase for the `create` action"""

    url_template = f"{SERVICE_URL}"
    http_method_name = "POST"
    success_code = 201

    def setUp(self):
        """Also prepares a valid payload"""
        super().setUp()
        self.payload = {
            "email": "fakeemail@fakedomain.com",
            "first_name": "FirstName",
            "last_name": "LastName",
            "password": "Str0ngEn0ugh",
            "confirm_password": "Str0ngEn0ugh",
            "is_active": True,
            "is_staff": True,
            "is_verified": False,
        }

    def test_permissions(self):
        """Tests it is only accessible to admin users"""
        self.assert_admin_permissions(self.url(), self.payload)

    def test_password_field(self):
        """Test the password strength"""
        self.assert_password_strength()

    def test_confirm_password_field(self):
        """Tests both passwords must match"""
        self.assert_matching_password()

    def test_success(self):
        """Tests we can successfully create a user"""
        response = self.http_method(self.url(), self.payload)
        assert response.status_code == self.success_code
        assert User.objects.count() == 2
        created_user = User.objects.get(id=2)
        self.assert_response_matches_objects(response.data, created_user, self.payload)


class TestAdminListUsers(Base):
    """TestCase for the `list` action"""

    url_template = f"{SERVICE_URL}"
    http_method_name = "GET"
    success_code = 200

    def test_permissions(self):
        """Tests it is only accessible to admin users"""
        self.assert_admin_permissions(self.url())

    def test_success(self):
        """Tests we can successfully retrieve our users"""
        response = self.http_method(self.url())
        assert response.status_code == self.success_code
        assert len(response.data) == 1
        user_2 = self.create_user()
        user_3 = self.create_user()
        response = self.http_method(self.url())
        assert response.status_code == self.success_code
        assert len(response.data) == 3
        for i, user in enumerate([self.admin, user_2, user_3]):
            instance = User.objects.get(id=i + 1)
            self.assert_response_matches_objects(response.data[2 - i], instance)


#
#
# class TestAdminRetrieveUser(Base):
#     url_template = f"{SERVICE_URL}/{{id}}/"
#     http_method_name = "GET"
#     success_code = 200
#
#     def test_permissions(self):
#         pass
#
#     def test_success(self):
#         pass
#
#
# class TestAdminUpdateUser(Base):
#     url_template = f"{SERVICE_URL}/{{id}}/"
#     http_method_name = "PUT"
#     success_code = 200
#
#     def test_permissions(self):
#         pass
#
#     def test_success(self):
#         pass
#
#
# class TestAdminDestroyUser(Base):
#     url_template = f"{SERVICE_URL}/{{id}}/"
#     http_method_name = "DELETE"
#     success_code = 204
#
#     def test_permissions(self):
#         pass
#
#     def test_success(self):
#         pass
#
#
# class TestAdminBulkDestroyUsers(Base):
#     url_template = f"{SERVICE_URL}"
#     http_method_name = "DELETE"
#     success_code = 204
#
#     def test_permissions(self):
#         pass
#
#     def test_success(self):
#         pass
#
#
# class TestAdminRequestVerification(Base):
#     url_template = f"{SERVICE_URL}"
#     http_method_name = "DELETE"
#     success_code = 200
#
#     def test_permissions(self):
#         pass
#
#     def test_already_verified(self):
#         pass
#
#     def test_success(self):
#         pass
#
#
# class TestAdminOverridePassword(Base):
#     url_template = f"{SERVICE_URL}"
#     http_method_name = "DELETE"
#     success_code = 204
#
#     def test_permissions(self):
#         pass
#
#     def test_password_field(self):
#         pass
#
#     def test_confirm_password_field(self):
#         pass
#
#     def test_success(self):
#         pass
