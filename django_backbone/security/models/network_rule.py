"""Rules to whitelist or blacklist IPs"""

# Built-in
from datetime import date, timedelta

# Django
from django.db.models import (
    DateField,
    GenericIPAddressField,
    Index,
    IntegerChoices,
    IntegerField,
)

# Personal
from jklib.django.db.fields import ActiveField, RequiredField, TrimCharField
from jklib.django.db.models import LifeCycleModel
from jklib.django.db.queries import get_object_or_none
from jklib.django.utils.network import get_client_ip
from jklib.django.utils.settings import get_config


# --------------------------------------------------------------------------------
# > Models
# --------------------------------------------------------------------------------
class NetworkRule(LifeCycleModel):
    """Model to blacklist or whitelist IP addresses"""

    # ----------------------------------------
    # Constants
    # ----------------------------------------
    # Static
    COMMENT_MAX_LENGTH = 255

    # Overridable
    DEFAULT_DURATION = 30  # settings.NETWORK_RULE_DEFAULT_DURATION

    # Statuses
    class Status(IntegerChoices):
        """Possible statuses for a NetworkRule"""

        NONE = 0
        WHITELISTED = 1
        BLACKLISTED = 2

    # ----------------------------------------
    # Fields
    # ----------------------------------------
    ip = RequiredField(
        GenericIPAddressField, protocol="IPv4", unique=True, verbose_name="IP Address",
    )
    status = RequiredField(
        IntegerField,
        choices=Status.choices,
        default=Status.NONE,
        verbose_name="Status",
        db_index=True,
    )
    expires_on = DateField(
        blank=True,
        null=True,
        default=None,
        db_index=True,  # clear_expired_entries
        verbose_name="Expires on",
        help_text="Expires at the end of said date",
    )
    active = ActiveField()
    comment = TrimCharField(
        max_length=COMMENT_MAX_LENGTH, blank=True, verbose_name="Comment"
    )

    # ----------------------------------------
    # Behavior (meta, str, save)
    # ----------------------------------------
    class Meta:
        db_table = "security_network_rules"
        indexes = [
            Index(fields=["active", "expires_on", "status"])  # For the `bulk_clear` API
        ]
        ordering = ["-id"]
        verbose_name = "Network Rule"
        verbose_name_plural = "Network Rules"

    def __str__(self):
        """
        :return: Returns the network rule's IP address
        :rtype: str
        """
        return f"{self.ip}"

    # ----------------------------------------
    # Properties
    # ----------------------------------------
    @classmethod
    def get_default_duration(cls):
        """
        :return: The default duration for a status, which can be overridden in the settings
        :rtype: int
        """
        return get_config("NETWORK_RULE_DEFAULT_DURATION", cls.DEFAULT_DURATION)

    @property
    def computed_status(self):
        """
        :return: The current state of the rule based on all its properties
        :rtype: str
        """
        if self.is_blacklisted:
            return "blacklisted"
        if self.is_whitelisted:
            return "whitelisted"
        return "inactive"

    @property
    def is_blacklisted(self):
        """
        :return: Whether the rule/IP is currently active and blacklisted
        :rtype: bool
        """
        check = self.active and self.status == self.Status.BLACKLISTED
        if self.expires_on is None:
            return check
        else:
            return check and self.expires_on >= date.today()

    @property
    def is_whitelisted(self):
        """
        :return: Whether the rule/IP is currently active and whitelisted
        :rtype: bool
        """
        check = self.active and self.status == self.Status.WHITELISTED
        if self.expires_on is None:
            return check
        else:
            return check and self.expires_on >= date.today()

    # ----------------------------------------
    # API for instance
    # ----------------------------------------
    def blacklist(self, end_date=None, comment=None, override=False):
        """
        Updates the instance to blacklist its IP address
        :param date end_date: The desired expiration date
        :param str comment: The comment to add in the instance
        :param bool override: Whether we allow blacklisting a whitelisted entry
        """
        self._update_status("blacklist", end_date, comment, override)

    def clear(self):
        """Clears the instance by defaulting its fields to neutral values"""
        self.expires_on = None
        self.active = False
        self.status = self.Status.NONE
        self.save()

    def whitelist(self, end_date=None, comment=None, override=False):
        """
        Updates the instance to whitelist its IP address
        :param date end_date: The desired expiration date
        :param str comment: The comment to add in the instance
        :param bool override: Whether we allow whitelisting a blacklisted entry
        """
        self._update_status("whitelist", end_date, comment, override)

    def _compute_valid_end_date(self, end_date):
        """
        Defaults the expiration date if none is provided
        :param date end_date: The desired expiration date
        :return: Either the provided date or the default one
        :rtype: date
        """
        if end_date is None:
            delta_in_days = timedelta(days=self.get_default_duration())
            end_date = date.today() + delta_in_days
        return end_date

    def _update_status(self, action, end_date, comment, override):
        """
        Update all the required fields to whitelist or blacklist the rule's IP
        :param str action: Action to perform, used to define the status check
        :param date end_date: The desired expiration date
        :param str comment: The comment to add in the instance
        :param bool override: Whether we allow whitelisting a blacklisted entry
        """
        if action == "whitelist":
            status_check = self.Status.BLACKLISTED
            new_status = self.Status.WHITELISTED
        else:
            status_check = self.Status.WHITELISTED
            new_status = self.Status.BLACKLISTED
        if override or self.status != status_check:
            if comment is not None:
                self.comment = comment
            self.expires_on = self._compute_valid_end_date(end_date)
            self.active = True
            self.status = new_status
            self.save()

    # ----------------------------------------
    # API for request
    # ----------------------------------------
    @classmethod
    def blacklist_from_request(
        cls, request, end_date=None, comment=None, override=False
    ):
        """
        Creates or updates a blacklist rule for the request's IP, and returns the instance.
        :param Request request: Request object used to get the IP address
        :param date end_date: The desired expiration date
        :param str comment: The comment to add in the instance
        :param bool override: Whether we allow blacklisting a whitelisted entry
        :return: The updated instance
        :rtype: NetworkRule
        """
        instance = cls._fetch_or_add(request)
        instance.blacklist(end_date, comment, override)
        return instance

    @classmethod
    def clear_from_request(cls, request):
        """
        If it exists, clears and returns the NetworkRule model
        :param Request request: Request object used to get the IP address
        :return: The updated instance
        :rtype: NetworkRule or None
        """
        instance = cls._fetch(request)
        if instance is not None:
            instance.clear()
        return instance

    @classmethod
    def whitelist_from_request(
        cls, request, end_date=None, comment=None, override=False
    ):
        """
        Creates or updates a whitelist rule for the request's IP, and returns the instance.
        :param Request request: Request object used to get the IP address
        :param date end_date: The desired expiration date
        :param str comment: The comment to add in the instance
        :param bool override: Whether we allow whitelisting a blacklisted entry
        :return: The updated instance
        :rtype: NetworkRule
        """
        instance = cls._fetch_or_add(request)
        instance.whitelist(end_date, comment, override)
        return instance

    @classmethod
    def is_blacklisted_from_request(cls, request):
        """
        Checks if a blacklisted NetworkRule linked to the request IP exists
        :param Request request: Request object that could be used to get/add the instance
        :return: Whether the IP is blacklisted
        :rtype: bool
        """
        instance = cls._fetch(request)
        if instance is not None:
            return instance.is_blacklisted
        return False

    @classmethod
    def is_whitelisted_from_request(cls, request):
        """
        Checks if a whitelisted NetworkRule linked to the request IP exists
        :param Request request: Request object that could be used to get/add the instance
        :return: Whether the IP is whitelisted
        :rtype: bool
        """
        instance = cls._fetch(request)
        if instance is not None:
            return instance.is_whitelisted
        return False

    @classmethod
    def _fetch(cls, request):
        """
        Fetches an existing NetworkRule instance using the Request object
        :param Request request: A django Request object
        :return: The existing instance linked to this IP
        :rtype: NetworkRule
        """
        ip_address = get_client_ip(request)
        instance = get_object_or_none(cls, ip=ip_address)
        return instance

    @classmethod
    def _fetch_or_add(cls, request):
        """
        Fetches an existing NetworkRule instance or create a new one using the Request object
        :param Request request: A django Request object
        :return: The found (or newly-added) NetworkRule instance
        :rtype: NetworkRule
        """
        ip_address = get_client_ip(request)
        instance = get_object_or_none(cls, ip=ip_address)
        if instance is None:
            instance = cls(ip=ip_address, active=False)
        return instance

    # ----------------------------------------
    # CRON jobs
    # ----------------------------------------
    @classmethod
    def clear_expired_entries(cls):
        """Clears all expired rules"""
        today = date.today()
        instances = cls.objects.filter(expires_on__isnull=False).filter(
            expires_on__lt=today
        )
        for instance in instances:
            instance.clear()
