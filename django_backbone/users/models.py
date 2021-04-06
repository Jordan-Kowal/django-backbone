"""Custom user model"""

# Built-in
from collections import namedtuple
from enum import Enum

# Django
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, UserManager
from django.db import models
from django.utils import timezone

# Personal
from jklib.django.utils.emails import send_html_email, send_html_email_async
from jklib.django.utils.network import build_url

# Application
from core.utils import render_email_template

# --------------------------------------------------------------------------------
# > Utilities
# --------------------------------------------------------------------------------
EmailInfo = namedtuple("EmailInfo", ["template", "subject", "endpoint"])


class UserEmailTemplate(EmailInfo, Enum):
    """List of email templates for our users"""

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


class EmailUserManager(UserManager):
    """Custom manager for a User model where the username is the email"""

    def _create_user(self, email, password, **extra_fields):
        """
        Correctly creates a user by checking its email and hashing its password
        :param str email:
        :param str password: raw (not hashed) value
        :return: The created instance
        :rtype: User
        """
        if not email:
            raise ValueError("The given username must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email=None, password=None, **extra_fields):
        """
        Creates a new user
        :param str email:
        :param str password: raw (not hashed) value
        :return: The created instance
        :rtype: User
        """
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_admin(self, email=None, password=None, **extra_fields):
        """
        Creates a new admin user
        :param str email:
        :param str password: raw (not hashed) value
        :return: The created instance
        :rtype: User
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", False)
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Admin user must have is_staff=True.")
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email=None, password=None, **extra_fields):
        """
        Creates a new superuser
        :param str email:
        :param str password: raw (not hashed) value
        :return: The created instance
        :rtype: User
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        return self._create_user(email, password, **extra_fields)


# --------------------------------------------------------------------------------
# > Models
# --------------------------------------------------------------------------------
class User(AbstractBaseUser, PermissionsMixin):
    """Custom user model where the email is the username"""

    # Base fields
    email = models.EmailField("Email address", blank=False, unique=True)
    first_name = models.CharField("First name", max_length=150, blank=True)
    last_name = models.CharField("Last name", max_length=150, blank=True)
    is_staff = models.BooleanField("Staff status", default=False, db_index=True)
    is_active = models.BooleanField("Active", default=True, db_index=True)
    date_joined = models.DateTimeField("Date joined", default=timezone.now)
    # Custom Fields
    is_verified = models.BooleanField("Verified", default=False, db_index=True)

    # Base settings
    objects = EmailUserManager()
    EMAIL_FIELD = "email"
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []  # Should not include the username field
    # Custom settings
    RESET_TOKEN = ("reset", 7200)  # 2 hours
    VERIFY_TOKEN = ("verify", 172800)  # 7 days

    class Meta:
        db_table = "users"
        indexes = []
        ordering = ["-id"]
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        """
        :return: The user's email address
        :rtype: str
        """
        return self.email

    def clean(self):
        """Also cleans the `email` field"""
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    @property
    def full_name(self):
        """
        :return: Concatenate the first and last names
        :rtype: str
        """
        return f"{self.first_name} {self.last_name}"

    # ----------------------------------------
    # Creation API
    # ----------------------------------------
    @classmethod
    def create_user(cls, email=None, password=None, **extra_fields):
        """
        Creates a new user
        :param str email:
        :param str password: raw (not hashed) value
        :return: The created instance
        :rtype: User
        """
        return cls.objects.create_user(email, password, **extra_fields)

    @classmethod
    def create_admin(cls, email=None, password=None, **extra_fields):
        """
        Creates a new admin user
        :param str email:
        :param str password: raw (not hashed) value
        :return: The created instance
        :rtype: User
        """
        return cls.objects.create_admin(email, password, **extra_fields)

    @classmethod
    def create_superuser(cls, email=None, password=None, **extra_fields):
        """
        Creates a new superuser
        :param str email:
        :param str password: raw (not hashed) value
        :return: The created instance
        :rtype: User
        """
        return cls.objects.create_superuser(email, password, **extra_fields)

    # ----------------------------------------
    # Email API
    # ----------------------------------------
    def send_email(self, template_path, subject, context=None, async_=True):
        """
        Shortcut to send an email to our user with additional context values
        :param str template_path: Django path to our email template
        :param str subject: Subject of the email
        :param dict context: Context values for the template rendering
        :param bool async_: Whether the email will be sent asynchronously. Defaults to True.
        """
        if context is None:
            context = {}
        context["user"] = self
        body = render_email_template(template_path, context)
        if async_:
            send_html_email_async(subject, body, to=self.email)
        else:
            send_html_email(subject, body, to=self.email)

    def send_password_updated_email(self, async_=True):
        """
        Sends the 'password_updated' email to our user
        :param bool async_: Whether the email will be sent asynchronously. Defaults to True.
        """
        email = UserEmailTemplate.PASSWORD_UPDATED
        self.send_email(
            template_path=email.template, subject=email.subject, async_=async_
        )

    def send_reset_password_email(self, token, async_=True):
        """
        Sends the 'reset_password' email to our user, which contains the reset link
        :param SecurityToken token: A valid RESET token
        :param bool async_: Whether the email will be sent asynchronously. Defaults to True.
        """
        self._check_token_before_email(token, self.RESET_TOKEN[0])
        email = UserEmailTemplate.REQUEST_PASSWORD_RESET
        context = {"password_reset_link": self._build_password_reset_url(token.value)}
        self.send_email(
            template_path=email.template,
            subject=email.subject,
            context=context,
            async_=async_,
        )

    def send_verification_email(self, token, async_=True):
        """
        Sends the 'verification_email' email to our user, which contains the verification link
        :param SecurityToken token: A valid VERIFY token
        :param bool async_: Whether the email will be sent asynchronously. Defaults to True.
        """
        self._check_token_before_email(token, self.VERIFY_TOKEN[0])
        if self.is_verified:
            return
        email = UserEmailTemplate.VERIFY_EMAIL
        context = {"verification_link": self._build_verification_url(token.value)}
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
        email = UserEmailTemplate.WELCOME
        self.send_email(
            template_path=email.template, subject=email.subject, async_=async_
        )

    # ----------------------------------------
    # Private
    # ----------------------------------------
    @staticmethod
    def _build_password_reset_url(token_value):
        """
        Builds the reset link for our user, using the frontend URL and the generated token
        :param str token_value: The value of our recently generated token
        :return: The frontend URL to reset your password
        :rtype: str
        """
        root_url = settings.FRONTEND_ROOT_URL
        relative_url = UserEmailTemplate.REQUEST_PASSWORD_RESET.endpoint
        params = {"token": token_value}
        parts = [root_url, relative_url]
        return build_url(parts, params=params)

    @staticmethod
    def _build_verification_url(token_value):
        """
        Builds the verification link for our user, using the frontend URL and the generated token
        :param str token_value: The value of our recently generated token
        :return: The frontend URL to verify your account
        :rtype: str
        """
        root_url = settings.FRONTEND_ROOT_URL
        relative_url = UserEmailTemplate.VERIFY_EMAIL.endpoint
        params = {"token": token_value}
        parts = [root_url, relative_url]
        return build_url(parts, params=params)

    def _check_token_before_email(self, token, expected_type):
        """
        Checks the token can be used in our email
        :param SecurityToken token: The token used for the email
        :param str expected_type: The type we need our token to be
        :raises ValueError: If token is not usable
        :raises TypeError: If token does not match the expected type
        """
        if not token.can_be_used:
            raise ValueError("Provided SecurityToken is not usable")
        if token.type != expected_type:
            raise TypeError(
                f"Received SecurityToken of type `{token.type}`. Expected `{expected_type}`"
            )
