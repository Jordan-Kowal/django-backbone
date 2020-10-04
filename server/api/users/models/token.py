"""Token"""

# Built-in
from datetime import datetime, timedelta, timezone
from secrets import token_urlsafe

# Django
from django.contrib.auth.models import User
from django.db.models import CharField, DateTimeField

# Personal
from jklib.django.db.fields import ActiveField, ForeignKeyCascade, RequiredField
from jklib.django.db.models import LifeCycleModel
from jklib.django.db.queries import get_object_or_none


class Token(LifeCycleModel):
    """
    Security tokens are unique, OTP, expiring tokens usable in our API
    They allow an unauthenticated user to perform actions, such as password reset or account verification

    The tokens abide by the following rules:
        They must be attached to a USER and a TYPE
        They have a short lifespan and will eventually expire
        A user may only have 1 active token per type (which is the only usable token)
        For a token to be valid, it must be active, not expired, and not used

    The basic workflow should be:
        create_new_token        --> Sets a new token                --> Returns the token instance and its value
        fetch_token_instance    --> Gets your token later on        --> Returns the token instance
        consume_token           --> Declares the token as used      --> Does not return anything

    Other useful methods are:
        cleanup_expired_unused_tokens   --> Useful as a CRON to clean up the database
        deactivate_token                --> When you want to preemptively kill a token
        deactivate_user_tokens          --> When you want to deactivate all the tokens of a user
    """

    # ----------------------------------------
    # Constants
    # ----------------------------------------
    MIN_DURATION = 300  # 5 minutes
    MAX_DURATION = 604800  # 7 days

    # ----------------------------------------
    # Fields
    # ----------------------------------------
    user = ForeignKeyCascade(User, related_name="tokens")
    type = RequiredField(CharField, max_length=50)
    value = RequiredField(CharField, unique=True, max_length=1000)
    expired_at = DateTimeField(null=False)
    used_at = DateTimeField(null=True)
    is_active_token = ActiveField()

    # ----------------------------------------
    # Meta, str, save, get_absolute_url
    # ----------------------------------------
    class Meta:
        """Meta class to setup our database table"""

        db_table = "tokens"
        indexes = []
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
    # Public API
    # ----------------------------------------
    @classmethod
    def cleanup_expired_unused_tokens(cls):
        """Deletes all the tokens that are expired and haven't been used"""
        now = datetime.now(timezone.utc)
        expired_unused_tokens = cls.objects.filter(used_at=None, expired_at__lt=now)
        expired_unused_tokens.delete()

    def consume_token(self):
        """Deactivates the token and stores its used timestamp"""
        self.used_at = datetime.now(timezone.utc)
        self.deactivate_token()

    @classmethod
    def create_new_token(cls, user, token_type, token_duration):
        """
        Creates a new unique token for the user/type which will be his only 'active' token
        All previous tokens related to the user/type are automatically deactivated
        Returns both the created token instance and its raw value
        :param User user: Instance from the User model
        :param str token_type: Type of the token
        :param int token_duration: Token lifespan in seconds
        :return: The token instance and its value
        :rtype: (Token, str)
        """
        token_value = cls._generate_unique_token()
        token_params = cls._get_valid_token_params(
            user, token_value, token_type, token_duration
        )
        cls.deactivate_user_tokens(user, token_params["type"])
        token_instance = cls.objects.create(**token_params)
        return token_instance, token_value

    def deactivate_token(self):
        """Marks a token as not being the active one anymore"""
        self.is_active_token = False
        self.save()

    @classmethod
    def deactivate_user_tokens(cls, user, token_type=None):
        """
        Fetches and deactivates all the tokens of our user for a given type
        If no type is specified, will be applied to all existing types
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
        Given a token value, will return the matching token instance if it is found and still valid
        For a token to be valid it must: be the active one, not be expired, not have been used
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
    # Private class methods
    # ----------------------------------------
    @classmethod
    def _generate_unique_token(cls):
        """
        Creates a new random token value until it is unique
        To check uniqueness, it compares its value to the database
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
        :return: The trimmed value, if valid
        :rtype: str
        """
        if type(value) != str:
            raise TypeError("Token type must be a string")
        value = value.strip()
        if value == "":
            raise ValueError("Token type cannot be empty")
        return value
