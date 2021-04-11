"""Tests for the User viewsets"""

# Built-in
from datetime import timedelta
from time import sleep

# Django
from django.utils import timezone

# Application
from core.tests import BaseActionTestCase
from security.models import SecurityToken

# Local
from ...factories import AdminFactory, UserFactory
from ...models import User, UserEmailTemplate

# --------------------------------------------------------------------------------
# > Helpers
# --------------------------------------------------------------------------------
SERVICE_URL = "/api/users/"


class Base(BaseActionTestCase):
    """Base class for testing the UserAdmin API"""

    def assert_password_strength(self, url, data):
        """
        Checks the password strength
        :param str url: URL of the endpoint
        :param dict data: The data for the request
        """
        self.payload["password"] = "test"
        self.payload["confirm_password"] = "test"
        response = self.http_method(url, data=data)
        assert response.status_code == 400
        assert len(response.data["password"]) > 0

    def assert_matching_password(self, url, data):
        """
        Checks both passwords must match
        :param str url: URL of the endpoint
        :param dict data: The data for the request
        """
        self.payload["password"] = "Str0ngEn0ugh"
        self.payload["confirm_password"] = "test"
        response = self.http_method(url, data=data)
        assert response.status_code == 400
        assert len(response.data["confirm_password"]) > 0

    def assert_token_field(self, url, user, token_type, token_duration, payload):
        """
        Checks that the service does not accept invalid tokens
        :param str url: URL of the endpoint
        :param User user: The user the token will belong to
        :param str token_type: Expected type of the token
        :param int token_duration: Standard duration of the token
        :param dict payload: A valid payload to be used in the request
        """
        # Token with wrong type
        wrong_type_toklen = SecurityToken.create_new_token(
            user, "wrong_type", token_duration
        )
        payload["token"] = wrong_type_toklen.value
        response = self.http_method(url, data=payload)
        assert response.status_code == 400
        assert len(response.data["token"]) > 0
        # Wrong value
        payload = {"token": "NotTheRightValue"}
        response = self.http_method(url, data=payload)
        assert response.status_code == 400
        assert len(response.data["token"]) > 0
        # Expired token
        expired_token = SecurityToken.create_new_token(user, token_type, token_duration)
        expired_token.expired_at = timezone.now() - timedelta(days=1)
        expired_token.save()
        payload = {"token": expired_token.value}
        response = self.http_method(url, data=payload)
        assert response.status_code == 400
        assert len(response.data["token"]) > 0
        # Not the active one
        token_1 = SecurityToken.create_new_token(user, token_type, token_duration)
        SecurityToken.create_new_token(user, token_type, token_duration)
        payload = {"token": token_1.value}
        response = self.http_method(url, data=payload)
        assert response.status_code == 400
        assert len(response.data["token"]) > 0

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
            assert response_data["is_verified"] == instance.is_verified
        if payload is not None:
            assert response_data["email"] == payload.get("email")
            assert response_data["first_name"] == payload.get("first_name", "")
            assert response_data["last_name"] == payload.get("last_name", "")


# --------------------------------------------------------------------------------
# > TestCases
# --------------------------------------------------------------------------------
class TestCreateUser(Base):
    """TestCase for the `create` action"""

    url_template = f"{SERVICE_URL}"
    http_method_name = "POST"
    success_code = 201

    def setUp(self):
        """Resets the email outbox and prepares a valid payload"""
        self.payload = {
            "email": "fakeemail@fakedomain.com",
            "first_name": "FirstName",
            "last_name": "LastName",
            "password": "Str0ngP4ssw0rd!",
            "confirm_password": "Str0ngP4ssw0rd!",
        }

    def test_permissions(self):
        """Tests only a non-authenticated user can call this service"""
        self.assert_not_authenticated_permissions(self.url(), self.payload)
        assert User.objects.count() == 3
        sleep(0.4)  # Due to emails being sent asynchronously

    def test_password_field(self):
        """Tests the password strength"""
        self.assert_password_strength(self.url(), self.payload)

    def test_confirm_password_field(self):
        """Tests both passwords must match"""
        self.assert_matching_password(self.url(), self.payload)

    def test_success(self):
        """Tests you can successfully create your account"""
        response = self.http_method(self.url(), data=self.payload)
        assert response.status_code == self.success_code
        assert User.objects.count() == 1
        user = User.objects.get(id=1)
        self.assert_response_matches_objects(response.data, user, self.payload)
        if not user.is_verified:
            subject = UserEmailTemplate.VERIFY_EMAIL.subject
        else:
            subject = UserEmailTemplate.WELCOME.subject
        self.assert_email_was_sent(subject, to=[user.email], async_=True)


class TestRetrieveUser(Base):
    """TestCase for the `retrieve` action"""

    url_template = f"{SERVICE_URL}/{{id}}/"
    http_method_name = "GET"
    success_code = 200

    def setUp(self):
        """Creates and authenticates a user, then prepares a URL"""
        self.user = UserFactory()
        self.api_client.force_authenticate(self.user)
        self.detail_url = self.url(context={"id": self.user.id})

    def test_permissions(self):
        """Tests only the user himself can fetch his data"""
        admin = AdminFactory()
        self.assert_owner_permissions(self.detail_url, owner=self.user, not_owner=admin)

    def test_success(self):
        """Tests the owner can retrieve his information"""
        response = self.http_method(self.detail_url)
        self.assert_response_matches_objects(response.data, self.user)


class TestUpdateUser(Base):
    """TestCase for the `update` action"""

    url_template = f"{SERVICE_URL}/{{id}}/"
    http_method_name = "PUT"
    success_code = 200

    def setUp(self):
        """Creates and authenticates a user, then prepares a URL and a payload"""
        self.user = UserFactory()
        self.api_client.force_authenticate(self.user)
        self.detail_url = self.url(context={"id": self.user.id})
        self.payload = {
            "email": "newfakeemail@thatdomain.com",
            "first_name": "NewFirstName",
            "last_name": "NewLastName",
        }

    def test_permissions(self):
        """Tests only the owner can updates his info"""
        admin = AdminFactory()
        self.assert_owner_permissions(
            self.detail_url, owner=self.user, not_owner=admin, data=self.payload
        )

    def test_success(self):
        """Tests the owner can successfully update his info"""
        response = self.http_method(self.detail_url, data=self.payload)
        assert response.status_code == self.success_code
        instance = User.objects.get(id=self.user.id)
        self.assert_response_matches_objects(response.data, instance, self.payload)


class TestDestroyUser(Base):
    """TestCase for the `destroy` action"""

    url_template = f"{SERVICE_URL}/{{id}}/"
    http_method_name = "DELETE"
    success_code = 204

    def setUp(self):
        """Creates and authenticates a user, then prepares a URL"""
        self.user = UserFactory()
        self.api_client.force_authenticate(self.user)
        self.detail_url = self.url(context={"id": self.user.id})

    def test_permissions(self):
        """Tests only the owner can delete himself"""
        admin = AdminFactory()
        self.assert_owner_permissions(self.detail_url, owner=self.user, not_owner=admin)

    def test_success(self):
        """Tests the owner can successfully delete himself"""
        response = self.http_method(self.detail_url)
        assert response.status_code == self.success_code
        assert response.data is None
        assert User.objects.count() == 0


class TestPerformPasswordReset(Base):
    """TestCase for the `perform_password_reset` action"""

    url_template = f"{SERVICE_URL}/perform_password_reset/"
    http_method_name = "POST"
    success_code = 204

    def setUp(self):
        """Creates a user, a token, and a valid payload"""
        self.initial_password = "Str0ngP4ssw0rd"
        self.user = UserFactory(password=self.initial_password)
        self.token_type, self.token_duration = User.RESET_TOKEN
        self.token = SecurityToken.create_new_token(
            self.user, self.token_type, self.token_duration
        )
        self.payload = {
            "password": "Str00ngP44ssw0rd!!",
            "confirm_password": "Str00ngP44ssw0rd!!",
            "token": self.token.value,
        }

    def test_permissions(self):
        """Tests only logged out users can use this service"""
        self.assert_not_authenticated_permissions(self.url(), data=self.payload)
        sleep(0.4)  # Waiting for emails to be sent

    def test_password(self):
        """Tests the new password must be strong enough"""
        self.assert_password_strength(self.url(), data=self.payload)

    def test_confirm_password(self):
        """Tests the passwords must match"""
        self.assert_matching_password(self.url(), data=self.payload)

    def test_token(self):
        """Tests the user must provide a valid and active RESET token"""
        self.assert_token_field(
            url=self.url(),
            user=self.user,
            token_type=self.token_type,
            token_duration=self.token_duration,
            payload=self.payload,
        )

    def test_success(self):
        """Tests the user's password gets updated and that he receives an email"""
        response = self.http_method(self.url(), data=self.payload)
        assert response.status_code == self.success_code
        assert response.data is None
        subject = UserEmailTemplate.PASSWORD_UPDATED.subject
        self.assert_email_was_sent(subject, to=[self.user.email], async_=True)
        updated_user = User.objects.get(id=self.user.id)
        assert updated_user.check_password(self.payload["password"])
        assert not updated_user.check_password(self.initial_password)


class TestPerformVerification(Base):
    """TestCase for the `perform_verification` action"""

    url_template = f"{SERVICE_URL}/perform_verification/"
    http_method_name = "POST"
    success_code = 204

    def setUp(self):
        """Registers the token type and duration"""
        self.token_type, self.token_duration = User.VERIFY_TOKEN

    def test_permissions(self):
        """Tests the service is accessible by anyone"""
        user = UserFactory()
        admin = AdminFactory()
        for instance in [None, user, admin]:
            self.api_client.logout()
            if instance is not None:
                self.api_client.force_authenticate(instance)
            else:
                instance = UserFactory()
            token = SecurityToken.create_new_token(
                instance, self.token_type, self.token_duration
            )
            payload = {"token": token.value}
            response = self.http_method(self.url(), data=payload)
            assert response.status_code == self.success_code
            assert response.data is None
        sleep(0.4)

    def test_token(self):
        """Tests the user must provide a valid and active VERIFY token"""
        user = UserFactory()
        payload = {}
        self.assert_token_field(
            url=self.url(),
            user=user,
            token_type=self.token_type,
            token_duration=self.token_duration,
            payload=payload,
        )

    def test_already_verified(self):
        """Tests no email is sent if the user was already verified"""
        user = UserFactory(is_verified=True)
        token = SecurityToken.create_new_token(
            user, self.token_type, self.token_duration
        )
        payload = {"token": token.value}
        response = self.http_method(self.url(), data=payload)
        assert response.status_code == self.success_code
        assert response.data is None
        with self.assertRaises((AssertionError, IndexError)):
            subject = UserEmailTemplate.WELCOME.subject
            self.assert_email_was_sent(subject, to=[user.email], async_=True)

    def test_success(self):
        """Tests the user gets verified, the email is sent, and the token is consumed"""
        user = UserFactory()
        token = SecurityToken.create_new_token(
            user, self.token_type, self.token_duration
        )
        payload = {"token": token.value}
        response = self.http_method(self.url(), data=payload)
        assert response.status_code == self.success_code
        assert response.data is None
        # Email has been sent
        subject = UserEmailTemplate.WELCOME.subject
        self.assert_email_was_sent(subject, to=[user.email], async_=True)
        # User has been updated
        updated_user = User.objects.get(id=user.id)
        assert updated_user.is_verified
        # Token has been consumed
        updated_token = SecurityToken.objects.get(id=token.id)
        assert updated_token.is_used
        assert not updated_token.is_active_token


class TestRequestPasswordReset(Base):
    """TestCase for the `request_password_reset` action"""

    url_template = f"{SERVICE_URL}/request_password_reset/"
    http_method_name = "POST"
    success_code = 202

    def setUp(self):
        """Creates a user and prepares a payload"""
        self.user = UserFactory()
        self.payload = {"email": self.user.email}

    def test_permissions(self):
        """Tests only a logged out user can use this service"""
        self.assert_not_authenticated_permissions(self.url(), self.payload)
        sleep(0.4)

    def test_unknown_email(self):
        """Tests the service returns OK if unknown user, but sends no email"""
        self.payload["email"] = "unknownemail@domain.com"
        response = self.http_method(self.url(), self.payload)
        assert response.status_code == self.success_code
        assert response.data is None
        with self.assertRaises((AssertionError, IndexError)):
            subject = UserEmailTemplate.REQUEST_PASSWORD_RESET.subject
            self.assert_email_was_sent(subject, to=[self.user.email], async_=True)

    def test_success(self):
        """Tests the server correctly sends an email to our user"""
        response = self.http_method(self.url(), self.payload)
        assert response.status_code == self.success_code
        assert response.data is None
        subject = UserEmailTemplate.REQUEST_PASSWORD_RESET.subject
        self.assert_email_was_sent(subject, to=[self.user.email], async_=True)


class TestRequestVerification(Base):
    """TestCase for the `request_verification` action"""

    url_template = f"{SERVICE_URL}/{{id}}/request_verification/"
    http_method_name = "POST"
    success_code = 204

    def setUp(self):
        """Creates and authenticates a user, then prepares a URL"""
        self.user = UserFactory()
        self.api_client.force_authenticate(self.user)
        self.detail_url = self.url(context={"id": self.user.id})

    def test_permissions(self):
        """Tests the user must be the owner and not already verified"""
        admin = AdminFactory()
        self.assert_owner_permissions(self.detail_url, self.user, admin)
        # If verified, should not work
        self.user.is_verified = True
        self.user.save()
        self.api_client.logout()
        self.api_client.force_authenticate(self.user)
        response = self.http_method(self.detail_url)
        assert response.status_code == 403
        sleep(0.4)

    def test_success(self):
        """Tests an unverified user can receive the verification email"""
        response = self.http_method(self.detail_url)
        assert response.status_code == self.success_code
        assert response.data is None
        subject = UserEmailTemplate.VERIFY_EMAIL.subject
        self.assert_email_was_sent(subject, to=[self.user.email], async_=True)


class TestUpdatePassword(Base):
    """TestCase for the `update_password` action"""

    url_template = f"{SERVICE_URL}/{{id}}/update_password/"
    http_method_name = "POST"
    success_code = 204

    def setUp(self):
        """Creates and authenticates a user, then prepares a URL and payload"""
        self.payload = {
            "current_password": "Str0ngP4ssw0rD!",
            "password": "Str0ngP4ssw0rD!!!",
            "confirm_password": "Str0ngP4ssw0rD!!!",
        }
        self.user = UserFactory(password=self.payload["current_password"])
        self.api_client.force_authenticate(self.user)
        self.detail_url = self.url(context={"id": self.user.id})

    def test_permissions(self):
        """Tests only the owner can reset his own password"""
        admin = AdminFactory(password=self.payload["current_password"])
        self.assert_owner_permissions(self.detail_url, self.user, admin, self.payload)
        sleep(0.4)  # For the email to be sent

    def test_current_password(self):
        """Tests the user must provide the correct current password"""
        self.payload["current_password"] = "invalidPassword"
        response = self.http_method(self.detail_url, data=self.payload)
        assert response.status_code == 400
        assert len(response.data["current_password"]) > 0

    def test_password(self):
        """Tests the user must provide a strong-enough new password"""
        self.assert_password_strength(self.detail_url, self.payload)

    def test_confirm_password(self):
        """Tests the confirmation password must match the new password"""
        self.assert_matching_password(self.detail_url, self.payload)

    def test_success(self):
        """Tests the user can successfully update his own password"""
        response = self.http_method(self.detail_url, data=self.payload)
        assert response.status_code == self.success_code
        # Check the password has been updated
        update_user = User.objects.get(id=self.user.id)
        assert not update_user.check_password(self.payload["current_password"])
        assert update_user.check_password(self.payload["password"])
        # Check the email was sent
        subject = UserEmailTemplate.PASSWORD_UPDATED.subject
        self.assert_email_was_sent(subject, to=[update_user.email], async_=True)
