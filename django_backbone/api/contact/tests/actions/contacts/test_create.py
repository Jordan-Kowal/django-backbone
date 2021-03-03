"""TestCase for the 'create' action"""

# Built-in
from datetime import date, timedelta
from time import sleep

# Django
from django.core import mail

# Personal
from jklib.django.drf.tests import ActionTestCase
from jklib.django.utils.settings import get_config

# Application
from api.network.models import NetworkRule

# Local
from ....models import Contact
from ._shared import BASE_URL


# --------------------------------------------------------------------------------
# > TestCase
# --------------------------------------------------------------------------------
class TestCreateContact(ActionTestCase):
    """TestCase for the 'create' action"""

    required_fields = [
        "name",
        "email",
        "subject",
        "body",
    ]
    service_base_url = f"{BASE_URL}/"
    success_code = 204

    # ----------------------------------------
    # Behavior
    # ----------------------------------------
    def setUp(self):
        """Creates a normal and admin user, and prepares a valid payload"""
        self.user = self.create_user()
        self.admin = self.create_admin_user()
        self.payload = {
            "name": self.generate_random_string(5, " ", 5),
            "email": self.generate_random_string(15, "@", 5, ".com"),
            "subject": self.generate_random_string(2, " ", 4, " ", 6),
            "body": self.generate_random_string(10, " ", 10, " ", 10),
            "notify_user": False,
        }

    # ----------------------------------------
    # Tests
    # ----------------------------------------
    def test_permissions(self):
        """Tests that all users can access this service"""
        # Not authenticated
        response = self.client.post(self.service_base_url, self.payload)
        assert response.status_code == self.success_code
        assert Contact.objects.count() == 1
        # As user
        self.client.force_authenticate(self.user)
        response = self.client.post(self.service_base_url, self.payload)
        assert response.status_code == self.success_code
        assert Contact.objects.count() == 2
        # As admin
        self.client.logout()
        self.client.force_authenticate(self.admin)
        response = self.client.post(self.service_base_url, self.payload)
        assert response.status_code == self.success_code
        assert Contact.objects.count() == 3

    def test_required_fields(self):
        """Tests that the required fields are truly required"""
        self.assert_fields_are_required(
            self.client.post, self.service_base_url, self.payload
        )
        assert Contact.objects.count() == 0

    def test_name(self):
        """Tests the 'name' field min and max allowed lengths"""
        invalid_names = self._generate_invalid_strings(*Contact.NAME_LENGTH)
        self._assert_invalid_values_for_field("name", invalid_names)

    def test_email(self):
        """Tests the 'email' field truly is an email"""
        invalid_emails = ["Not an email", 33]
        self._assert_invalid_values_for_field("email", invalid_emails)

    def test_subject(self):
        """Tests the 'subject' field min and max allowed lengths"""
        invalid_subjects = self._generate_invalid_strings(*Contact.SUBJECT_LENGTH)
        self._assert_invalid_values_for_field("subject", invalid_subjects)

    def test_body(self):
        """Tests the 'body' field min and max allowed lengths"""
        invalid_body = self._generate_invalid_strings(*Contact.BODY_LENGTH)
        self._assert_invalid_values_for_field("body", invalid_body)

    def test_notify_user_default(self):
        """Tests the user does not receive an email if the argument is missing"""
        del self.payload["notify_user"]
        response = self.client.post(self.service_base_url, self.payload)
        assert response.status_code == self.success_code
        assert Contact.objects.count() == 1
        sleep(0.2)
        assert len(mail.outbox) == 1

    def test_automatic_blacklisting(self):
        """Tests that the IP gets blacklisting if too many requests are sent"""
        ban_settings = Contact.get_ban_settings()
        threshold = ban_settings["threshold"]
        # No threshold, no ban
        if not threshold:
            response = self.client.post(self.service_base_url, self.payload)
            assert response.status_code == self.success_code
            contact = Contact.objects.last()
            assert not contact.should_ban_ip()
        else:
            # Reach the threshold
            [
                self.client.post(self.service_base_url, self.payload)
                for _ in range(threshold)
            ]
            assert Contact.objects.count() == threshold
            # Should be eligible for ban
            contact = Contact.objects.last()
            assert contact.should_ban_ip()
            # Create one too many. It should fail
            response = self.client.post(self.service_base_url, self.payload)
            assert response.status_code == 403
            assert Contact.objects.count() == threshold
            # The IP should now be banned using our settings
            network_rule = NetworkRule.objects.get(ip=contact.ip)
            expected_end_date = date.today() + timedelta(
                days=ban_settings["duration_in_days"]
            )
            assert network_rule.is_blacklisted
            assert network_rule.expires_on == expected_end_date
            # Any new request should fail due to the ban
            response = self.client.post(self.service_base_url, self.payload)
            assert response.status_code == 403

    def test_success(self):
        """Tests a successful contact without notifying the user"""
        self._assert_successful_creation(self.payload)
        sleep(0.2)
        assert len(mail.outbox) == 1
        email = mail.outbox[0]
        assert email.subject == Contact.EmailTemplate.ADMIN_NOTIFICATION.subject
        assert email.to[0] == get_config("EMAIL_HOST_USER")

    def test_success_with_email(self):
        """Tests a successful contact and sends an email to the user"""
        self.payload["notify_user"] = True
        self._assert_successful_creation(self.payload)
        # 2 emails should have been sent
        sleep(0.4)
        assert len(mail.outbox) == 2
        email_1, email_2 = mail.outbox[0], mail.outbox[1]
        subjects = [email_1.subject, email_2.subject]
        recipients = [email_1.to[0], email_2.to[0]]
        assert Contact.EmailTemplate.ADMIN_NOTIFICATION.subject in subjects
        assert Contact.EmailTemplate.USER_NOTIFICATION.subject in subjects
        assert self.payload["email"] in recipients
        assert get_config("EMAIL_HOST_USER") in recipients

    def test_success_with_user(self):
        """Tests the user instance is stored if the request was sent while authenticated"""
        self.client.force_authenticate(self.user)
        instance = self._assert_successful_creation(self.payload)
        assert instance.user == self.user

    # ----------------------------------------
    # Helpers
    # ----------------------------------------
    def _assert_successful_creation(self, payload):
        """
        Creates and returns a Contact using the service and the provided payload
        Also checks the instance has the right values
        :param dict payload: The values to send to the service
        :return: The created Contact instance
        :rtype: Contact
        """
        quantity = Contact.objects.count()
        response = self.client.post(self.service_base_url, payload)
        assert response.status_code == self.success_code
        assert Contact.objects.count() == quantity + 1
        instance = Contact.objects.last()
        # Check the instance values
        assert instance.name == payload["name"]
        assert instance.email == payload["email"]
        assert instance.subject == payload["subject"]
        assert instance.body == payload["body"]
        assert instance.ip != ""
        assert instance.ip is not None
        return instance

    def _assert_invalid_values_for_field(self, field, values):
        """
        Assigns invalid values to a field and checks if the service failed
        :param str field: Name of the field to override
        :param [*] values: List of invalid values to test
        """
        initial_count = Contact.objects.count()
        for value in values:
            self.payload[field] = value
            response = self.client.post(self.service_base_url, self.payload)
            self.assert_field_has_error(response, field)
        assert Contact.objects.count() == initial_count

    def _generate_invalid_strings(self, min_, max_):
        """
        Generates and returns a list of invalid strings. More specifically:
        Empty string, whitespace string, too short, too long
        :param int min_: The min length requirement
        :param int max_: The max length requirement
        :return: The generated strings
        :rtype: [str]
        """
        return [
            "",
            " " * min_,
            self.generate_random_string(min_ - 1),
            self.generate_random_string(max_ + 1),
        ]
