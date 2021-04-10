"""Tokens for one-time use"""

# Built-in
from datetime import datetime, timedelta, timezone
from secrets import token_urlsafe

# Django
from django.contrib.auth import get_user_model
from django.db.models import CharField, DateTimeField, Index

# Personal
from jklib.django.db.fields import ActiveField, ForeignKeyCascade, RequiredField
from jklib.django.db.models import LifeCycleModel
from jklib.django.db.queries import get_object_or_none


# --------------------------------------------------------------------------------
# > Models
# --------------------------------------------------------------------------------
class SecurityToken(LifeCycleModel):
    """
    Tokens are OTP linked to users, to allow for special actions like password reset
        Only 1 active token per user/type
        Token have a limited duration/lifespan
        Can only be used once

    The expected workflow of the model API is:
        create_new_token        --> Creates a new token for a user/type
        fetch_token_instance    --> Fetches the Token instance linked to your token value
        consume_token           --> Token won't be usable anymore

    Other utilities for clean up and security are also available
    """

    # ----------------------------------------
    # Constants
    # ----------------------------------------
    MIN_DURATION = 300  # 5 minutes
    MAX_DURATION = 604800  # 7 days
    TYPE_MAX_LENGTH = 50

    # ----------------------------------------
    # Fields
    # ----------------------------------------
    user = RequiredField(
        ForeignKeyCascade, get_user_model(), related_name="tokens", verbose_name="User"
    )
    type = RequiredField(CharField, max_length=TYPE_MAX_LENGTH, verbose_name="Type")
    value = RequiredField(
        CharField, unique=True, max_length=1000, verbose_name="Token value"
    )
    expired_at = RequiredField(DateTimeField, verbose_name="Expires at")
    used_at = DateTimeField(null=True, blank=True, verbose_name="Used at")
    is_active_token = ActiveField()

    # ----------------------------------------
    # Behavior (meta, str, save)
    # ----------------------------------------
    class Meta:
        db_table = "security_tokens"
        indexes = [
            Index(fields=["user", "type", "is_active_token"]),  # deactivate_user_tokens
            Index(fields=["type", "value"]),  # fetch_token_instance
            Index(fields=["used_at", "expired_at"]),  # cleanup_expired_unused_tokens
        ]
        ordering = ["-id"]
        verbose_name = "Token"
        verbose_name_plural = "Tokens"

    def __str__(self):
        """
        :return: Returns the token value
        :rtype: str
        """
        return f"{self.value}"

    # ----------------------------------------
    # Properties
    # ----------------------------------------
    @property
    def can_be_used(self):
        """
        :return: Checks if the token is active, not used, and not expired
        :rtype: bool
        """
        return self.is_active_token and (not self.is_used) and (not self.is_expired)

    @property
    def is_expired(self):
        """
        :return: Whether the token has expired
        :rtype: bool
        """
        now = datetime.now(timezone.utc)
        return self.expired_at < now

    @property
    def is_used(self):
        """
        :return: Whether the token has been used
        :rtype: bool
        """
        return self.used_at is not None

    # ----------------------------------------
    # Public API
    # ----------------------------------------
    def consume_token(self):
        """Deactivates the token and stores its used timestamp"""
        self.used_at = datetime.now(timezone.utc)
        self.deactivate_token()

    @classmethod
    def create_new_token(cls, user, token_type, token_duration):
        """
        Creates a new token for the user/type, and deactivates the previous ones
        :param User user: Instance from the User model
        :param str token_type: Type of the token
        :param int token_duration: Token lifespan in seconds
        :return: The token instance and its value
        :rtype: SecurityToken
        """
        token_value = cls._generate_unique_token()
        token_params = cls._get_valid_token_params(
            user, token_value, token_type, token_duration
        )
        cls.deactivate_user_tokens(user, token_params["type"])
        token_instance = cls.objects.create(**token_params)
        return token_instance

    def deactivate_token(self):
        """Marks a token as not being the active one anymore"""
        self.is_active_token = False
        self.save()

    @classmethod
    def deactivate_user_tokens(cls, user, token_type=None):
        """
        Deactivates all tokens for a user. Can be narrowed down to a specific type.
        :param User user: The user whose tokens must be deactivated
        :param str token_type: Type of the token. Defaults to None
        """
        tokens = cls.objects.filter(user=user, is_active_token=True)
        if token_type is not None:
            tokens = tokens.filter(type=token_type)
        for token in tokens:
            token.deactivate_token()

    @classmethod
    def fetch_token_instance(cls, token_value, token_type):
        """
        Tries to fetch an ACTIVE Token instance using a token value and type
        :param str token_value: Value of the token
        :param str token_type: Type of the token
        :return: The valid token instance or None
        :rtype: Token or None
        """
        token = get_object_or_none(cls, value=token_value, type=token_type)
        if token is not None and token.can_be_used:
            return token
        else:
            return None

    # ----------------------------------------
    # Cron jobs
    # ----------------------------------------
    @classmethod
    def cleanup_expired_unused_tokens(cls):
        """Deletes all the tokens that are expired and haven't been used"""
        now = datetime.now(timezone.utc)
        expired_unused_tokens = cls.objects.filter(used_at=None, expired_at__lt=now)
        expired_unused_tokens.delete()

    # ----------------------------------------
    # Private
    # ----------------------------------------
    @classmethod
    def _generate_unique_token(cls):
        """
        :return: The unique value to be used for creating a new token
        :rtype: str
        """
        while True:
            token_value = token_urlsafe(50)
            results = cls.objects.filter(value=token_value)
            if len(results) == 0:
                break
        return token_value

    @classmethod
    def _get_valid_token_params(cls, user, token_value, token_type, token_duration):
        """
        Validates (and replaces if necessary) the parameters for creating a new token
        :param User user: Instance of the User model
        :param str token_value: Value of the token, which should be unique
        :param str token_type: Type of the token
        :param int token_duration: Token lifespan
        :return: Parameters to be used for creating a new token
        :rtype: dict
        """
        token_type = cls._validate_token_type(token_type)
        token_duration = cls._validate_token_duration(token_duration)
        expiration_date = datetime.now(timezone.utc) + timedelta(seconds=token_duration)
        return {
            "user": user,
            "type": token_type,
            "value": token_value,
            "expired_at": expiration_date,
            "used_at": None,
            "is_active_token": True,
        }

    @classmethod
    def _validate_token_duration(cls, value):
        """
        Returns the initial duration is a valid integer, else raises an error
        :param int value: Duration of the token in seconds
        :raise TypeError: When the provided value is not an integer
        :raise ValueError: When the provided value is out of bounds
        :return: The initial value, if valid
        :rtype: int
        """
        if type(value) != int:
            raise TypeError("Token duration must be an integer")
        if value < cls.MIN_DURATION or value > cls.MAX_DURATION:
            raise ValueError(
                f"Token duration must be between {cls.MIN_DURATION} and {cls.MAX_DURATION} seconds"
            )
        return value

    @classmethod
    def _validate_token_type(cls, value):
        """
        Returns the initial type if it is a non-empty string, else raises an error
        :param str value: Type of the token
        :raise TypeError: When the provided value is a string
        :raise ValueError: When the provided value is empty
        :return: The trimmed value, if valid
        :rtype: str
        """
        if type(value) != str:
            raise TypeError("Token type must be a string")
        value = value.strip()
        if value == "":
            raise ValueError("Token type cannot be empty")
        return value
