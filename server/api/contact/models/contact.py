"""Contact"""


# Built-in
from datetime import date, timedelta

# Django
from django.conf import settings
from django.core.validators import MinLengthValidator
from django.db.models import (
    CharField,
    EmailField,
    GenericIPAddressField,
    Model,
    TextField,
)

# Personal
from jklib.django.db.fields import DateCreatedField, RequiredField
from jklib.django.utils.emails import get_css_content, send_html_email
from jklib.django.utils.network import get_server_domain
from jklib.django.utils.templates import render_template


# --------------------------------------------------------------------------------
# > Models
# --------------------------------------------------------------------------------
class Contact(Model):
    """Contact messages sent to our application"""

    # ----------------------------------------
    # Email templates
    # ----------------------------------------
    EMAILS = {
        "user_notification": {
            "template": "common/emails/user_notification.html",
            "subject": "Your message has been sent",
        },
        "admin_notification": {
            "template": "common/emails/admin_notification.html",
            "subject": "You have received a new message",
        },
    }

    # ----------------------------------------
    # Fields
    # ----------------------------------------
    created_at = DateCreatedField()
    ip = RequiredField(GenericIPAddressField, db_index=True, verbose_name="IP Address",)
    name = RequiredField(
        CharField,
        max_length=100,
        validators=[MinLengthValidator(3)],
        verbose_name="Name",
    )
    email = RequiredField(EmailField, verbose_name="Email",)
    subject = RequiredField(
        CharField,
        max_length=50,
        validators=[MinLengthValidator(3)],
        verbose_name="Subject",
    )
    body = RequiredField(
        TextField,
        max_length=2000,
        validators=[MinLengthValidator(10)],
        verbose_name="Body",
    )

    # ----------------------------------------
    # META, str, save, get_absolute_url
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
        """Returns the message subject"""
        return self.subject

    # ----------------------------------------
    # Custom methods
    # ----------------------------------------
    @classmethod
    def clean_old_records(cls):
        """Deletes records whose retention time is expired"""
        delta = timedelta(days=settings.CONTACT_RECORD_DURATION_IN_DAYS)
        max_date = date.today() - delta
        old_entries = Contact.objects.filter(date_create__lt=max_date)
        old_entries.delete()

    def send_email_notifications(self):
        """Notifies both the user and the designated admin that a contact request has been sent"""
        self._admin_alert_email()
        self._user_confirm_email()

    # ----------------------------------------
    # Private custom methods
    # ----------------------------------------
    def _admin_alert_email(self):
        """Sends an email to the main admin indicating a new contact was requested"""
        subject = "Vous avez reçu un nouveau message"
        template = settings.CONTACT_EMAIL_TEMPLATES["alert"]
        self._send_email(template, subject, settings.EMAIL_HOST_USER)

    def _send_email(self, template, subject, to):
        """
        Description:
            Method in charge of sending emails. Uses a preset context
        Args:
            template (str): Path the the HTML template used as the email
            subject (str): Subject of the email
            to (str): Main recipient of the email
        """
        domain = get_server_domain()
        contact_admin_url = (
            domain + "admin/api.contact/contact/" + str(self.id) + "/change"
        )
        context = {
            "contact": self,
            "contact_admin_url": contact_admin_url,
            "css": get_css_content("common/css/emails.css"),
            "domain": domain,
        }
        body = render_template(template, context)
        send_html_email(subject, body, to)

    def _user_confirm_email(self):
        """Sends a confirmation email to the user, following his contact request"""
        subject = "Votre message a bien été envoyée"
        template = settings.CONTACT_EMAIL_TEMPLATES["confirm"]
        self._send_email(template, subject, self.email)
