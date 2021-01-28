"""Contact"""

# Built-in
from collections import namedtuple
from datetime import timedelta
from enum import Enum

# Django
from django.contrib.auth.models import User
from django.db.models import SET_NULL, EmailField, ForeignKey, GenericIPAddressField
from django.utils import timezone

# Personal
from jklib.django.db.fields import RequiredField, TrimCharField, TrimTextField
from jklib.django.db.models import LifeCycleModel
from jklib.django.db.validators import LengthValidator
from jklib.django.utils.emails import send_html_email_async
from jklib.django.utils.settings import get_config

# Application
from api.core.utils import render_email_template

# --------------------------------------------------------------------------------
# > Helpers
# --------------------------------------------------------------------------------
EmailInfo = namedtuple("EmailInfo", ["template", "subject"])


# --------------------------------------------------------------------------------
# > Models
# --------------------------------------------------------------------------------
class Contact(LifeCycleModel):
    """
    Contact messages sent by our users through the API
    Class has been split into the following sub-sections:
        Constants
        Fields
        Behavior
        Validation
        Properties
        Public API
        CRON jobs
        Private methods
    """

    # ----------------------------------------
    # Constants
    # ----------------------------------------
    # Emails
    class EmailTemplate(EmailInfo, Enum):
        """Enum of namedtuples that store our email template data"""

        USER_NOTIFICATION = EmailInfo(
            "contact/emails/user_notification.html", "Your message has been sent"
        )
        ADMIN_NOTIFICATION = EmailInfo(
            "contact/emails/admin_notification.html", "New message received"
        )

    # Static
    BODY_LENGTH = [10, 2000]
    NAME_LENGTH = [3, 50]
    SUBJECT_LENGTH = [3, 50]

    # Overridable
    DEFAULT_RETENTION_DAYS = 30  # settings.CONTACT_RETENTION_DAYS
    DEFAULT_API_BAN_SETTINGS = {  # settings.CONTACT_API_BAN_SETTINGS
        "threshold": 3,
        "period_in_days": 30,
        "duration_in_days": 30,
    }

    # ----------------------------------------
    # Fields
    # ----------------------------------------
    ip = RequiredField(GenericIPAddressField, db_index=True, verbose_name="IP Address",)
    user = ForeignKey(
        User, on_delete=SET_NULL, null=True, blank=True, related_name="contacts"
    )
    name = RequiredField(
        TrimCharField,
        max_length=NAME_LENGTH[1],
        validators=[LengthValidator(*NAME_LENGTH)],
        verbose_name="Name",
    )
    email = RequiredField(EmailField, verbose_name="Email")
    subject = RequiredField(
        TrimCharField,
        max_length=SUBJECT_LENGTH[1],
        validators=[LengthValidator(*SUBJECT_LENGTH)],
        verbose_name="Subject",
    )
    body = RequiredField(
        TrimTextField, validators=[LengthValidator(*BODY_LENGTH)], verbose_name="Body",
    )

    # ----------------------------------------
    # Behavior (meta, str, save)
    # ----------------------------------------
    class Meta:
        """Meta class to setup the model"""

        db_table = "contacts"
        indexes = []
        ordering = ["-id"]
        unique_together = []
        verbose_name = "Contact"
        verbose_name_plural = "Contacts"

    def __str__(self):
        """
        :return: The instance subject
        :rtype: str
        """
        return self.subject

    # ----------------------------------------
    # Properties
    # ----------------------------------------
    @property
    def has_expired(self):
        """
        :return: Whether the Contact instance has expired (should be removed from the database)
        :rtype: bool
        """
        expiration_date = self.created_at + timedelta(days=self.get_retention_days())
        return expiration_date < timezone.now()

    @classmethod
    def get_ban_settings(cls):
        """
        :return: The API ban config for the Contact model, with custom override
        :rtype: dict
        """
        custom_config = get_config("CONTACT_API_BAN_SETTINGS", {})
        default_config = cls.DEFAULT_API_BAN_SETTINGS.copy()
        default_config.update(custom_config)
        return default_config

    @classmethod
    def get_retention_days(cls):
        """
        :return: The number of days a Contact instance is kept in the database
        :rtype: int
        """
        return get_config("CONTACT_RETENTION_DAYS", cls.DEFAULT_RETENTION_DAYS)

    # ----------------------------------------
    # Public API
    # ----------------------------------------
    def send_notifications(self, to_admin, to_user):
        """
        Sends notification emails to inform of a new contact message
        :param bool to_admin: Whether the admin should receive a notification
        :param bool to_user: Whether the user should receive a notification
        """
        if to_admin:
            admin_email = get_config("EMAIL_HOST_USER")
            self._send_async_email(self.EmailTemplate.ADMIN_NOTIFICATION, admin_email)
        if to_user:
            self._send_async_email(self.EmailTemplate.USER_NOTIFICATION, self.email)

    def should_ban_ip(self):
        """
        Checks if an IP should be banned based on the amount of contact requests recently sent
        If true, it means the ban would happen at the next API call
        :return: Whether it should be banned
        :rtype: bool
        """
        ban_settings = self.get_ban_settings()
        threshold = ban_settings["threshold"]
        # No threshold means no ban
        if not threshold:
            return False
        # Else we check
        creation_date_threshold = timezone.now() - timedelta(
            days=ban_settings["period_in_days"]
        )
        count = self.__class__.objects.filter(
            ip=self.ip, created_at__gt=creation_date_threshold
        ).count()
        return count >= threshold

    # ----------------------------------------
    # CRON jobs
    # ----------------------------------------
    @classmethod
    def remove_old_entries(cls):
        """Based on the retention days, remove overdue entries"""
        creation_limit = timezone.now() - timedelta(days=cls.get_retention_days())
        Contact.objects.filter(created_at__lt=creation_limit).delete()

    # ----------------------------------------
    # Private methods
    # ----------------------------------------
    def _send_async_email(self, email_template, to):
        """
        Sends an email to a target recipient, based on the provided template
        :param EmailTemplate email_template: The EmailTemplate to use
        :param str to: The recipient email address
        """
        context = {"contact": self}
        body = render_email_template(email_template.template, context)
        send_html_email_async(email_template.subject, body, to=to)
