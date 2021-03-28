"""Tests for the 'contact' app models"""

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
from ..models import Contact


# --------------------------------------------------------------------------------
# > TestCase
# --------------------------------------------------------------------------------
class TestContact(ModelTestCase):
    """TestCase for the 'Contact' model"""

    model_class = Contact

    # ----------------------------------------
    # Behavior
    # ----------------------------------------
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
        admin_email = get_config("EMAIL_HOST_USER")
        # No mail
        contact.send_notifications(False, False)
        sleep(0.2)
        assert len(mail.outbox) == 0
        # Only admin
        contact.send_notifications(True, False)
        sleep(0.2)
        email = mail.outbox[0]
        assert len(mail.outbox) == 1
        assert email.subject == contact.EmailTemplate.ADMIN_NOTIFICATION.subject
        assert len(email.to) == 1
        assert email.to[0] == admin_email
        # Only user
        contact.send_notifications(False, True)
        sleep(0.2)
        email = mail.outbox[1]
        assert len(mail.outbox) == 2
        assert email.subject == contact.EmailTemplate.USER_NOTIFICATION.subject
        assert len(email.to) == 1
        assert email.to[0] == contact.email
        # Both
        contact.send_notifications(True, True)
        sleep(0.4)
        email_1 = mail.outbox[2]
        email_2 = mail.outbox[3]
        subjects = {email_1.subject, email_2.subject}
        assert len(mail.outbox) == 4
        assert contact.EmailTemplate.ADMIN_NOTIFICATION.subject in subjects
        assert contact.EmailTemplate.USER_NOTIFICATION.subject in subjects
        recipients = [email_1.to[0], email_2.to[0]]
        assert len(email_1.to) == len(email_2.to) == 1
        assert admin_email in recipients
        assert contact.email in recipients

    def test_should_ban_ip(self):
        """Tests that we correctly check if an IP should be banned based on the settings"""
        ban_settings = Contact.get_ban_settings()
        threshold = ban_settings["threshold"]
        ip = self.payload["ip"]
        # No threshold, no ban
        if not threshold:
            self.model_class.objects.create(**self.payload)
            assert not self.model_class.should_ban_ip(ip)
        # Reach the threshold and check the ban
        else:
            for i in range(threshold - 1):
                self.model_class.objects.create(**self.payload)
                assert not self.model_class.should_ban_ip(ip)
            self.model_class.objects.create(**self.payload)  # Reach the threshold
            assert self.model_class.should_ban_ip(ip)

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
