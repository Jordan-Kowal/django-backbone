"""
Description:
    All the models used in this app
Models:
    Contact: Stores the contact requests made through the website contact form
"""


# Built-in
from datetime import date, timedelta

# Django
from django.conf import settings
from django.core.validators import MinLengthValidator
from django.db import models

# Personal
from jklib.django.db.fields import DateCreatedField
from jklib.django.utils.emails import get_css_content, send_html_email
from jklib.django.utils.network import get_server_domain
from jklib.django.utils.templates import render_template


# --------------------------------------------------------------------------------
# > Models
# --------------------------------------------------------------------------------
class Contact(models.Model):
    """Stores the contact requests made through the website contact form"""

    # ----------------------------------------
    # Settings
    # ----------------------------------------
    RECORD_DURATION = 30  # days

    # ----------------------------------------
    # Fields
    # ----------------------------------------
    created_at = DateCreatedField()
    ip = models.GenericIPAddressField(
        blank=False, db_index=True, null=False, verbose_name="Adresse IP",
    )
    name = models.CharField(
        blank=False,
        max_length=100,
        null=False,
        validators=[MinLengthValidator(3)],
        verbose_name="Nom",
    )
    company = models.CharField(
        blank=True,
        max_length=100,
        null=False,
        validators=[MinLengthValidator(3)],
        verbose_name="Société",
    )
    email = models.EmailField(blank=False, null=False, verbose_name="Email",)
    subject = models.CharField(
        blank=False,
        max_length=100,
        null=False,
        validators=[MinLengthValidator(3)],
        verbose_name="Objet",
    )
    message = models.TextField(
        blank=False,
        max_length=2000,
        null=False,
        validators=[MinLengthValidator(10)],
        verbose_name="Message",
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
    def delete_old_entries(cls):
        """Deletes the old record in the database, for security & privacy reasons"""
        delta = timedelta(days=cls.RECORD_DURATION)
        max_date = date.today() - delta
        old_entries = Contact.objects.filter(date_create__lt=max_date)
        old_entries.delete()

    def send_contact_emails(self, to_admin=True, to_user=True):
        """
        Description:
            Sends automatic emails after an contact has been created/sent
        Args:
            to_admin (bool): Whether the admin gets an alert email. Defaults to True.
            to_user (bool): Whether the user gets a confirmation email. Defaults to True.
        """
        if to_admin:
            self._admin_alert_email()
        if to_user:
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
