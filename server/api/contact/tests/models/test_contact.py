"""Tests for the 'Contact' model"""

# Built-in
from datetime import timedelta
from time import sleep

# Django
from django.conf import settings
from django.core import mail
from django.utils import timezone

# Personal
from jklib.django.db.tests import ModelTestCase
from jklib.django.utils.settings import get_config

# Local
from ...models import Contact


# --------------------------------------------------------------------------------
# > TestCase
# --------------------------------------------------------------------------------
class TestContact(ModelTestCase):
    """
    TestCase for the 'Contact' model
    Split into the following sections:
        Behavior
        Field tests
        Properties tests
        Public API
        Cron tests
        Helpers
    """

    model_class = Contact
    required_fields = [
        "ip",
        "email",
        "subject",
        "body",
    ]

    # ----------------------------------------
    # Behavior
    # ----------------------------------------
    @classmethod
    def setUpClass(cls):
        """Not implemented"""
        pass

    def setUp(self):
        """Creates a valid payload for a Contact instance"""
        self.payload = {
            "ip": "128.0.0.1",
            "user": None,
            "name": "Jordan Kowal",
            "email": "fakeemail@fakedomain.fakecom",
            "subject": "Fake subject",
            "body": "Fake body but long enough",
        }

    def tearDown(self):
        """Not implemented"""
        pass

    @classmethod
    def tearDownClass(cls):
        """Not implemented"""
        pass

    # ----------------------------------------
    # Field tests
    # ----------------------------------------
    def test_required_fields(self):
        """Tests that required fields are truly required"""
        self.assert_fields_are_required(self.payload)
        self.assert_instance_count_equals(0)

    def test_ip(self):
        """Tests the IP address must be in a valid format"""
        self.payload["ip"] = "Invalid IP"
        with self.assertRaises(self.common_errors):
            self.model_class(**self.payload).save()
        self.assert_instance_count_equals(0)

    def test_user(self):
        """Tests that the user field only accepts user instances"""
        # Not user
        self.payload["user"] = "Invalid User"
        with self.assertRaises(self.common_errors):
            self.model_class(**self.payload).save()
        self.assert_instance_count_equals(0)
        # With user
        self.payload["user"] = self.create_user()
        self.model_class(**self.payload).save()
        self.assert_instance_count_equals(1)

    def test_name(self):
        """Tests that the 'name' field must be of a certain length"""
        self._assert_field_length_error(
            payload=self.payload,
            field="name",
            min_=self.model_class.NAME_LENGTH[0],
            max_=self.model_class.NAME_LENGTH[1],
        )
        self.assert_instance_count_equals(0)

    def test_email(self):
        """Tests that the 'email' must be a valid format"""
        for invalid_email in ["invalid@email", 33]:
            self.payload["email"] = invalid_email
            with self.assertRaises(self.common_errors):
                self.model_class(**self.payload).save()
        self.assert_instance_count_equals(0)

    def test_subject(self):
        """Tests that the 'subject' field must be of a certain length"""
        self._assert_field_length_error(
            payload=self.payload,
            field="subject",
            min_=self.model_class.SUBJECT_LENGTH[0],
            max_=self.model_class.SUBJECT_LENGTH[1],
        )
        self.assert_instance_count_equals(0)

    def test_body(self):
        """Tests that the 'body' field must be of a certain length"""
        self._assert_field_length_error(
            payload=self.payload,
            field="body",
            min_=self.model_class.BODY_LENGTH[0],
            max_=self.model_class.BODY_LENGTH[1],
        )
        self.assert_instance_count_equals(0)

    def test_successful_creation(self):
        """Tests that we can successfully create a contact instance with and without user"""
        self.model_class(**self.payload).save()
        self.assert_instance_count_equals(1)
        user = self.create_user()
        self.payload["user"] = user
        self.model_class(**self.payload).save()
        self.assert_instance_count_equals(2)

    # ----------------------------------------
    # Properties tests
    # ----------------------------------------
    def test_get_ban_settings(self):
        """Tests the ban_settings returns the correct value based on the config"""
        contact = self.model_class.objects.create(**self.payload)
        ban_settings = contact.get_ban_settings()
        default_settings = contact.DEFAULT_API_BAN_SETTINGS
        overridden_settings = get_config("CONTACT_API_BAN_SETTINGS", {})
        for key in self.model_class.DEFAULT_API_BAN_SETTINGS.keys():
            value = overridden_settings.get(key, default_settings[key])
            assert value == ban_settings[key]

    def test_has_expired(self):
        """Tests that the expiration check is correctly computed"""
        contact = self.model_class.objects.create(**self.payload)
        retention_days = contact.get_retention_days()
        # Expired
        expired_date = timezone.now() - timedelta(days=retention_days + 1)
        contact.created_at = expired_date
        contact.save()
        assert contact.has_expired
        # Not expired
        non_expired_date = timezone.now() - timedelta(days=retention_days - 1)
        contact.created_at = non_expired_date
        contact.save()
        assert not contact.has_expired

    def test_get_retention_days(self):
        """Tests the retention_days returns the correct value based on the config"""
        contact = self.model_class.objects.create(**self.payload)
        retention_days = contact.get_retention_days()
        if hasattr(settings, "CONTACT_RETENTION_DAYS"):
            assert retention_days == settings.CONTACT_RETENTION_DAYS
        else:
            assert retention_days == contact.DEFAULT_RETENTION_DAYS

    # ----------------------------------------
    # Public API
    # ----------------------------------------
    def test_send_notifications(self):
        """Tests that notification emails are correctly sent"""
        contact = self.model_class.objects.create(**self.payload)
        # No mail
        contact.send_notifications(False, False)
        assert len(mail.outbox) == 0
        # Only admin
        contact.send_notifications(True, False)
        sleep(0.2)
        email = mail.outbox[0]
        assert len(mail.outbox) == 1
        assert email.subject == contact.EmailTemplate.ADMIN_NOTIFICATION.subject
        # Only user
        contact.send_notifications(False, True)
        sleep(0.2)
        email = mail.outbox[1]
        assert len(mail.outbox) == 2
        assert email.subject == contact.EmailTemplate.USER_NOTIFICATION.subject
        # Both
        contact.send_notifications(True, True)
        sleep(0.4)
        email_1 = mail.outbox[2]
        email_2 = mail.outbox[3]
        subjects = {email_1.subject, email_2.subject}
        assert len(mail.outbox) == 4
        assert contact.EmailTemplate.ADMIN_NOTIFICATION.subject in subjects
        assert contact.EmailTemplate.USER_NOTIFICATION.subject in subjects

    def test_should_ban_ip(self):
        """Tests that we correctly check if an IP should be banned based on the settings"""
        contact = self.model_class.objects.create(**self.payload)
        ban_settings = contact.get_ban_settings()
        threshold = ban_settings["threshold"]
        # No threshold, no ban
        if threshold is None or threshold == 0:
            assert not contact.test_should_ban_ip
        # Reach the threshold and check the ban
        else:
            for i in range(1, threshold):
                instance = self.model_class.objects.create(**self.payload)
                assert not instance.should_ban_ip()
            self.model_class.objects.create(**self.payload)  # One too many
            for instance in self.model_class.objects.all():
                assert instance.should_ban_ip()

    # ----------------------------------------
    # Cron tests
    # ----------------------------------------
    def test_remove_old_entries(self):
        """Tests that only expired entries are removed by the CRON job"""
        # Prepare the data
        instances = [self.model_class.objects.create(**self.payload) for i in range(10)]
        retention_days = instances[0].get_retention_days()
        self.assert_instance_count_equals(10)
        # Update dates for our instances
        expired_date = timezone.now() - timedelta(days=retention_days + 1)
        non_expired_date = timezone.now() - timedelta(days=retention_days - 1)
        for i in range(10):
            instance = instances[i]
            instance.created_at = expired_date if i < 4 else non_expired_date
            instance.save()
        # Call the job
        self.model_class.remove_old_entries()
        self.assert_instance_count_equals(6)

    # ----------------------------------------
    # Helpers
    # ----------------------------------------
    def _assert_field_length_error(self, payload, field, min_, max_):
        """
        Tests that a specific field with the given min/max lengths generates an error on creation
        :param dict payload: A valid payload that could be used to create a instance
        :param str field: The field to override and test
        :param int min_: The minimal length accepted
        :param int max_: The maximum length accepted
        """
        empty_value = ""
        short_value = "a" * (min_ - 1)
        long_value = "a" * (max_ + 1)
        for value in [empty_value, short_value, long_value]:
            self.payload[field] = value
            with self.assertRaises(self.common_errors):
                self.model_class(**payload).save()
