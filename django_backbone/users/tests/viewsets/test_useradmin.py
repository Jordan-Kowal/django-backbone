"""Tests for the User-related viewsets"""

# Personal
from jklib.django.drf.tests import ActionTestCase

# Application
# --------------------------------------------------------------------------------
# > Helpers
# --------------------------------------------------------------------------------
from users.models import User, UserEmailTemplate

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


class TestAdminRetrieveUser(Base):
    """TestCase for the `retrieve` action"""

    url_template = f"{SERVICE_URL}/{{id}}/"
    http_method_name = "GET"
    success_code = 200

    def setUp(self):
        """Also creates an additional user"""
        super().setUp()
        self.user = self.create_user()
        self.detail_url = self.url(context={"id": self.user.id})

    def test_permissions(self):
        """Tests it is only accessible to admin users"""
        self.assert_admin_permissions(self.detail_url)

    def test_success(self):
        """Tests we can successfully retrieve one user"""
        response = self.http_method(self.detail_url)
        assert response.status_code == self.success_code
        self.assert_response_matches_objects(response.data, self.user)


class TestAdminUpdateUser(Base):
    """TestCase for the `update` action"""

    url_template = f"{SERVICE_URL}/{{id}}/"
    http_method_name = "PUT"
    success_code = 200

    def setUp(self):
        """Also creates an additional user and an update payload"""
        super().setUp()
        self.user = self.create_user()
        self.detail_url = self.url(context={"id": self.user.id})
        self.payload = {
            "email": "fakeemail@fakedomain.com",
            "first_name": "FirstName",
            "last_name": "LastName",
            "is_active": True,
            "is_staff": True,
            "is_verified": False,
        }

    def test_permissions(self):
        """Tests it is only accessible to admin users"""
        self.assert_admin_permissions(self.detail_url, payload=self.payload)

    def test_success(self):
        """Tests we can successfully update a user"""
        response = self.http_method(self.detail_url, data=self.payload)
        assert response.status_code == self.success_code
        update_user = User.objects.get(id=self.user.id)
        self.assert_response_matches_objects(response.data, update_user, self.payload)


class TestAdminDestroyUser(Base):
    """TestCase for the `destroy` action"""

    url_template = f"{SERVICE_URL}/{{id}}/"
    http_method_name = "DELETE"
    success_code = 204

    def setUp(self):
        """Also creates an additional user"""
        super().setUp()
        self.user = self.create_user()
        self.detail_url = self.url(context={"id": self.user.id})

    def test_permissions(self):
        """Tests it is only accessible to admin users"""
        self.assert_admin_permissions(self.detail_url)

    def test_success(self):
        """Tests we can successfully delete a user"""
        assert User.objects.count() == 2
        response = self.http_method(self.detail_url)
        assert response.status_code == self.success_code
        assert response.data is None
        assert User.objects.count() == 1


class TestAdminBulkDestroyUsers(Base):
    """TestCase for the `bulk_destroy` action"""

    url_template = f"{SERVICE_URL}"
    http_method_name = "DELETE"
    success_code = 204

    def setUp(self):
        """Also creates 5 additional users"""
        super().setUp()
        for i in range(5):
            self.create_user()

    def test_permissions(self):
        """Tests it is only accessible to admin users"""
        payload = {"ids": [2, 3, 5]}
        assert User.objects.count() == 6
        self.assert_admin_permissions(self.url(), payload=payload)
        # The function created 2 users and we deleted 3, so total is -1
        assert User.objects.count() == 5

    def test_success(self):
        """Tests we can successfully delete multiple users at once"""
        assert User.objects.count() == 6
        # Only valid IDs
        payload = {"ids": [2, 3, 6]}
        response = self.http_method(self.url(), data=payload)
        assert response.status_code == self.success_code
        assert response.data is None
        assert User.objects.count() == 3
        # Some valid IDs
        payload = {"ids": [5, 10]}
        response = self.http_method(self.url(), data=payload)
        assert response.status_code == self.success_code
        assert response.data is None
        assert User.objects.count() == 2
        assert User.objects.first().id == 4
        assert User.objects.last().id == 1


class TestAdminRequestVerification(Base):
    """TestCase for the `request_verification` action"""

    url_template = f"{SERVICE_URL}/{{id}}/request_verification/"
    http_method_name = "POST"
    success_code = 204

    def setUp(self):
        """Also creates 1 additional user"""
        super().setUp()
        self.user = self.create_user()
        self.detail_url = self.url(context={"id": self.user.id})

    def test_permissions(self):
        """Tests it is only accessible to admin users"""
        self.assert_admin_permissions(self.detail_url)

    def test_already_verified(self):
        """Tests no email is sent if the user is already verified"""
        self.user.is_verified = True
        self.user.save()
        response = self.http_method(self.detail_url)
        assert response.status_code == 422
        assert response.data is None
        with self.assertRaises((AssertionError, IndexError)):
            subject = UserEmailTemplate.VERIFY_EMAIL.subject
            self.assert_email_was_sent(subject, to=[self.user.email], async_=True)

    def test_success(self):
        """Tests an unverified user can receive the verification email"""
        self.user.is_verified = False
        self.user.save()
        response = self.http_method(self.detail_url)
        assert response.status_code == self.success_code
        assert response.data is None
        subject = UserEmailTemplate.VERIFY_EMAIL.subject
        self.assert_email_was_sent(subject, to=[self.user.email], async_=True)
