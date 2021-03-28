"""Tests for the 'contact' app viewsets"""

# Built-in
from datetime import date, timedelta
from time import sleep

# Django
from django.core import mail

# Personal
from jklib.django.drf.tests import ActionTestCase
from jklib.django.utils.settings import get_config

# Application
from api.security.models import NetworkRule

# Local
from ..models import Contact

# --------------------------------------------------------------------------------
# > Helpers
# --------------------------------------------------------------------------------
SERVICE_URL = "/api/contacts/"


class Base(ActionTestCase):
    """Base class for all the Contact action test cases"""

    def setUp(self):
        """Creates and authenticates an Admin user"""
        self.admin = self.create_admin_user(authenticate=True)

    @staticmethod
    def assert_instance_representation(instance, response_data):
        """
        Compares a response data with a Contact instance
        :param Contact instance: Contact instance from the database
        :param dict response_data: Response data from the API
        """
        assert instance.id == response_data["id"]
        assert instance.ip == response_data["ip"]
        assert instance.name == response_data["name"]
        assert instance.email == response_data["email"]
        assert instance.subject == response_data["subject"]
        assert instance.body == response_data["body"]
        if instance.user is not None:
            user_data = response_data["user"]
            assert instance.user.id == user_data["id"]
            assert instance.user.first_name == user_data["first_name"]
            assert instance.user.last_name == user_data["last_name"]
            assert instance.user.email == user_data["email"]
            assert instance.user.is_active == user_data["is_active"]
            profile_data = user_data["profile"]
            assert instance.user.profile.is_verified == profile_data["is_verified"]
        else:
            assert response_data["user"] is None
        assert "notify_user" not in response_data

    @staticmethod
    def assert_payload_matches_instance(payload, instance):
        """
        Checks that the instance data matches it's original request payload
        :param dict payload: The request payload to create/update the contact demand
        :param Contact instance: The related Contact instance
        :return:
        """
        assert payload["name"] == instance.name
        assert payload["email"] == instance.email
        assert payload["subject"] == instance.subject
        assert payload["body"] == instance.body

    @staticmethod
    def create_contact(**kwargs):
        """
        Creates and returns a contact instance
        :param kwargs: Parameters to override the default values
        :return: The created Contact instance
        :rtype: Contact
        """
        default_values = {
            "ip": "127.0.0.1",
            "user": None,
            "name": "Name",
            "email": "fake-email@fake-domain.com",
            "subject": "Subject",
            "body": "Sufficiently long body",
        }
        data = {**default_values, **kwargs}
        return Contact.objects.create(**data)


# --------------------------------------------------------------------------------
# > TestCases
# --------------------------------------------------------------------------------
class TestCreateContact(Base):
    """TestCase for the 'list' action"""

    url_template = SERVICE_URL
    http_method_name = "POST"
    success_code = 204

    def setUp(self):
        """Also prepares a valid creation payload"""
        super().setUp()
        self.payload = {
            "name": "Name",
            "email": "fake-email@fake-domain.com",
            "subject": "Subject",
            "body": "Sufficiently long body",
            "notify_user": False,
        }

    def test_permissions(self):
        """Tests anybody can access this service"""
        user = self.create_user()
        admin = self.create_user()
        # Logged out
        self.api_client.logout()
        response = self.http_method(self.url(), data=self.payload)
        assert response.status_code == self.success_code
        # User
        self.api_client.force_authenticate(user)
        response = self.http_method(
            self.url(), data=self.payload, REMOTE_ADDR="127.0.0.2"
        )
        assert response.status_code == self.success_code
        # User
        self.api_client.logout()
        self.api_client.force_authenticate(admin)
        response = self.http_method(
            self.url(), data=self.payload, REMOTE_ADDR="127.0.0.3"
        )
        assert response.status_code == self.success_code
        assert Contact.objects.count() == 3

    def test_automatic_ban(self):
        """Tests that spamming contacts gets your IP banned"""
        ip = "127.0.0.2"
        ban_settings = Contact.get_ban_settings()
        threshold = ban_settings["threshold"]
        # Never banned
        if not threshold:
            response = self.http_method(self.url(), self.payload)
            assert response.status_code == self.success_code
            assert not Contact.should_ban_ip(ip=ip)
            return
        # Could be banned
        [
            self.http_method(self.url(), self.payload, REMOTE_ADDR=ip)
            for _ in range(threshold)
        ]
        assert Contact.objects.count() == threshold
        with self.assertLogs(logger="security", level="INFO") as logger:
            response = self.http_method(self.url(), self.payload, REMOTE_ADDR=ip)
            assert response.status_code == 403
            assert Contact.objects.count() == threshold
            # Check the associated NetworkRule
            rule = NetworkRule.objects.get(ip=ip)
            message = f"INFO:security:NetworkRule created for {rule.ip} (Status: {rule.computed_status})"
            assert logger.output[0] == message
            # Our IP should be blacklisted
            expected_end_date = date.today() + timedelta(
                days=ban_settings["duration_in_days"]
            )
            assert rule.is_blacklisted
            assert rule.expires_on == expected_end_date
        # Any subsequent request should fail
        response = self.http_method(self.url(), self.payload, REMOTE_ADDR=ip)
        assert response.status_code == 403
        # Other IPs can pass through
        response = self.http_method(self.url(), self.payload)
        assert response.status_code == self.success_code

    def test_success_notifications(self):
        """Tests that successful Contact creations send notifications"""
        # Without notification
        self._assert_creation_success_base(self.payload, 1)
        assert Contact.objects.count() == 1
        sleep(0.2)
        assert len(mail.outbox) == 1
        email = mail.outbox[0]
        assert email.subject == Contact.EmailTemplate.ADMIN_NOTIFICATION.subject
        assert email.to[0] == get_config("EMAIL_HOST_USER")
        # With notification
        mail.outbox = []
        self.payload["notify_user"] = True
        self._assert_creation_success_base(self.payload, 2)
        assert Contact.objects.count() == 2
        sleep(0.4)
        assert len(mail.outbox) == 2
        email_1, email_2 = mail.outbox[0], mail.outbox[1]
        subjects = [email_1.subject, email_2.subject]
        recipients = [email_1.to[0], email_2.to[0]]
        assert Contact.EmailTemplate.ADMIN_NOTIFICATION.subject in subjects
        assert Contact.EmailTemplate.USER_NOTIFICATION.subject in subjects
        assert self.payload["email"] in recipients
        assert get_config("EMAIL_HOST_USER") in recipients

    def test_success_user(self):
        """Tests that the User is correctly attached to the created Contact"""
        # Logged user
        instance = self._assert_creation_success_base(self.payload, 1)
        assert Contact.objects.count() == 1
        assert instance.user.id == self.admin.id
        # No user
        self.api_client.logout()
        instance = self._assert_creation_success_base(self.payload, 2)
        assert Contact.objects.count() == 2
        assert instance.user is None

    def test_success_ip(self):
        """Tests that the IP is correctly computed from the request"""
        ip = "127.0.0.3"
        instance = self._assert_creation_success_base(self.payload, 1, REMOTE_ADDR=ip)
        assert Contact.objects.count() == 1
        assert instance.ip == ip

    def _assert_creation_success_base(self, payload, id_, **params):
        """
        Performs a creation request and checks its success
        :param payload: The data to pass to our request
        :param int id_: The expected id of the created instance
        :param params: Extra parameters for the called method
        :return: The created Contact instance
        :rtype: Contact
        """
        response = self.http_method(self.url(), data=payload, **params)
        assert response.status_code == self.success_code
        instance = Contact.objects.get(id=id_)
        self.assert_payload_matches_instance(payload, instance)
        return instance


class TestListContacts(Base):
    """TestCase for the 'list' action"""

    url_template = SERVICE_URL
    http_method_name = "GET"
    success_code = 200

    def test_permissions(self):
        """Tests only admins can access this service"""
        self.assert_admin_permissions(self.url())

    def test_success(self):
        """Tests we can successfully fetch the list of Contact instances"""
        response = self.http_method(self.url())
        assert response.status_code == self.success_code
        assert Contact.objects.count() == len(response.data) == 0
        contact_1 = self.create_contact()
        contact_2 = self.create_contact(name="Name 2")
        response = self.http_method(self.url())
        assert response.status_code == self.success_code
        assert Contact.objects.count() == len(response.data) == 2
        self.assert_instance_representation(contact_2, response.data[0])
        self.assert_instance_representation(contact_1, response.data[1])


class TestRetrieveContact(Base):
    """TestCase for the 'retrieve' action"""

    url_template = f"{SERVICE_URL}/{{id}}/"
    http_method_name = "GET"
    success_code = 200

    def setUp(self):
        """Also creates a Contact instance"""
        super().setUp()
        self.contact = self.create_contact()
        self.detail_url = self.url(context={"id": self.contact.id})

    def test_permissions(self):
        """Tests only admins can access this service"""
        self.assert_admin_permissions(self.detail_url)

    def test_success(self):
        """Tests we can successfully retrieve a single Contact instance"""
        response = self.http_method(self.detail_url)
        assert response.status_code == self.success_code
        self.assert_instance_representation(self.contact, response.data)


class TestUpdateContact(Base):
    """TestCase for the 'update' action"""

    url_template = f"{SERVICE_URL}/{{id}}/"
    http_method_name = "PUT"
    success_code = 200

    def test_not_implemented(self):
        """Tests that this service is not implemented"""
        contact = self.create_contact()
        contact_url = self.url(context={"id": contact.id})
        response = self.http_method(contact_url, data=None)
        assert response.status_code == 405


class TestDestroyContact(Base):
    """TestCase for the 'destroy' action"""

    url_template = f"{SERVICE_URL}/{{id}}/"
    http_method_name = "DELETE"
    success_code = 204

    def setUp(self):
        """Also creates 2 Contact instances"""
        super().setUp()
        self.contact_1 = self.create_contact()
        self.contact_2 = self.create_contact(name="Name 2")
        self.url_1 = self.url(context={"id": self.contact_1.id})
        self.url_2 = self.url(context={"id": self.contact_2.id})

    def test_permissions(self):
        """Tests only admins can access this service"""
        assert Contact.objects.count() == 2
        self.assert_admin_permissions(self.url_1)
        assert Contact.objects.count() == 1

    def test_success(self):
        """Tests we can successfully delete individual Contact instances"""
        assert Contact.objects.count() == 2
        response = self.http_method(self.url_1)
        assert response.status_code == self.success_code
        assert Contact.objects.count() == 1
        response = self.http_method(self.url_2)
        assert response.status_code == self.success_code
        assert Contact.objects.count() == 0


class TestBulkDestroyContacts(Base):
    """TestCase for the 'bulk_destroy' action"""

    url_template = SERVICE_URL
    http_method_name = "DELETE"
    success_code = 204

    def setUp(self):
        """Also creates 4 Contact instances"""
        super().setUp()
        [setattr(self, f"contact_{i}", self.create_contact()) for i in range(1, 5)]
        self.payload = {"ids": [1, 4]}

    def test_permissions(self):
        """Tests only admins can access this service"""
        assert Contact.objects.count() == 4
        self.assert_admin_permissions(url=self.url(), payload=self.payload)
        assert Contact.objects.count() == 2

    def test_success(self):
        """Tests we can successfully delete multiple Contact instances at once"""
        # Only valid IDs
        response = self.http_method(self.url(), data=self.payload)
        assert response.status_code == self.success_code
        assert Contact.objects.count() == 2
        # Some valid IDs
        response = self.http_method(self.url(), data={"ids": [2, 6]})
        assert response.status_code == self.success_code
        assert Contact.objects.count() == 1
        assert Contact.objects.first().id == Contact.objects.last().id == 3
