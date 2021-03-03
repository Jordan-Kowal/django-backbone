"""Profile"""

# Built-in
from collections import namedtuple
from enum import Enum

# Django
from django.conf import settings
from django.contrib.auth.models import User
from django.db.models import CASCADE, BooleanField, Model, OneToOneField

# Personal
from jklib.django.db.fields import RequiredField
from jklib.django.utils.emails import send_html_email, send_html_email_async
from jklib.django.utils.network import build_url

# Application
from api.core.utils import render_email_template

# Local
from .token import Token

# --------------------------------------------------------------------------------
# > Helpers
# --------------------------------------------------------------------------------
EmailInfo = namedtuple("EmailInfo", ["template", "subject", "endpoint"])


# --------------------------------------------------------------------------------
# > Models
# --------------------------------------------------------------------------------
class Profile(Model):
    """
    Extends the User model to provide additional and utility to our User
    Split into the following sub-sections:
        Constants
        Fields
        Behavior
        Public API
        Private methods
    """

    # ----------------------------------------
    # Constants
    # ----------------------------------------
    class EmailTemplate(EmailInfo, Enum):
        """Enum of namedtuples that store our email template data"""

        PASSWORD_UPDATED = EmailInfo(
            "users/emails/password_updated.html", "Your password has been updated", None
        )
        REQUEST_PASSWORD_RESET = EmailInfo(
            "users/emails/request_password_reset.html", "Reset your password", "reset"
        )
        VERIFY_EMAIL = EmailInfo(
            "users/emails/verification_email.html",
            "Please verify your email address",
            "verify",
        )
        WELCOME = EmailInfo("users/emails/welcome.html", "Welcome", None)

    RESET_TOKEN = ("reset", 7200)  # 2 hours
    VERIFY_TOKEN = ("verify", 172800)  # 7 days

    # ----------------------------------------
    # Fields
    # ----------------------------------------
    user = RequiredField(
        OneToOneField,
        User,
        on_delete=CASCADE,
        related_name="profile",
        verbose_name="User",
    )
    is_verified = BooleanField(
        blank=True,
        default=False,
        null=False,
        verbose_name="Verified",
    )

    # ----------------------------------------
    # Behavior (meta, str, save)
    # ----------------------------------------
    class Meta:
        """Meta class to setup our model"""

        db_table = "users_profiles"
        indexes = []
        ordering = ["-id"]
        unique_together = []
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"

    def __str__(self):
        """
        :return: A string containing the username
        :rtype: str
        """
        return f"{self.user.username}'s profile"

    # ----------------------------------------
    # Public API
    # ----------------------------------------
    def send_email(self, template_path, subject, context=None, async_=True):
        """
        Shortcut to send an email to our user with additional context values
        By default, emails are sent asynchronously
        :param str template_path: Django path to our email template
        :param str subject: Subject of the email
        :param dict context: Context values for the template rendering
        :param bool async_: Whether the email will be sent asynchronously. Defaults to True.
        """
        if context is None:
            context = {}
        context["user"] = self.user
        body = render_email_template(template_path, context)
        if async_:
            send_html_email_async(subject, body, to=self.user.email)
        else:
            send_html_email(subject, body, to=self.user.email)

    def send_password_updated_email(self, async_=True):
        """
        Sends the 'password_updated' email to our user
        :param bool async_: Whether the email will be sent asynchronously. Defaults to True.
        """
        email = self.EmailTemplate.PASSWORD_UPDATED
        self.send_email(
            template_path=email.template, subject=email.subject, async_=async_
        )

    def send_reset_password_email(self, async_=True):
        """
        Sends the 'reset_password' email to our user, which contains the reset link
        :param bool async_: Whether the email will be sent asynchronously. Defaults to True.
        """
        token_type, token_duration = self.RESET_TOKEN
        _, token_value = self._create_token(token_type, token_duration)
        email = self.EmailTemplate.REQUEST_PASSWORD_RESET
        context = {"password_reset_link": self._build_password_reset_url(token_value)}
        self.send_email(
            template_path=email.template,
            subject=email.subject,
            context=context,
            async_=async_,
        )

    def send_verification_email(self, async_=True):
        """
        Sends the 'verification_email' email to our user, which contains the verification link
        Note that the email will be sent only if the user is not already verified
        :param bool async_: Whether the email will be sent asynchronously. Defaults to True.
        """
        if self.is_verified:
            return
        token_type, token_duration = self.VERIFY_TOKEN
        _, token_value = self._create_token(token_type, token_duration)
        email = self.EmailTemplate.VERIFY_EMAIL
        context = {"verification_link": self._build_verification_url(token_value)}
        self.send_email(
            template_path=email.template,
            subject=email.subject,
            context=context,
            async_=async_,
        )

    def send_welcome_email(self, async_=True):
        """
        Sends the 'welcome' email to our user
        :param bool async_: Whether the email will be sent asynchronously. Defaults to True.
        """
        email = self.EmailTemplate.WELCOME
        self.send_email(
            template_path=email.template, subject=email.subject, async_=async_
        )

    # ----------------------------------------
    # Private methods
    # ----------------------------------------
    def _build_password_reset_url(self, token_value):
        """
        Builds the reset link for our user, using the frontend URL and the generated token
        :param str token_value: The value of our recently generated token
        :return: The frontend URL to reset your password
        :rtype: str
        """
        root_url = settings.FRONTEND_ROOT_URL
        relative_url = self.EmailTemplate.REQUEST_PASSWORD_RESET.endpoint
        params = {"token": token_value}
        parts = [root_url, relative_url]
        return build_url(parts, params=params)

    def _build_verification_url(self, token_value):
        """
        Builds the verification link for our user, using the frontend URL and the generated token
        :param str token_value: The value of our recently generated token
        :return: The frontend URL to verify your account
        :rtype: str
        """
        root_url = settings.FRONTEND_ROOT_URL
        relative_url = self.EmailTemplate.VERIFY_EMAIL.endpoint
        params = {"token": token_value}
        parts = [root_url, relative_url]
        return build_url(parts, params=params)

    def _create_token(self, token_type, token_duration):
        """
        Creates a new unique token
        :param str token_type: Type of the token
        :param int token_duration: Lifespan of the token, in seconds
        :return: Both the instance and its value
        :rtype: (Token, str)
        """
        token_instance, token_value = Token.create_new_token(
            self.user, token_type, token_duration
        )
        return token_instance, token_value
