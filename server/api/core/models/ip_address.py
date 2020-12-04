"""IP Addresses"""

# Built-in
from datetime import date, timedelta

# Django
from django.db.models import (
    CharField,
    DateField,
    GenericIPAddressField,
    IntegerChoices,
    IntegerField,
)

# Personal
from jklib.django.db.fields import ActiveField, RequiredField
from jklib.django.db.models import LifeCycleModel
from jklib.django.db.queries import get_object_or_none
from jklib.django.utils.network import get_client_ip
from jklib.django.utils.settings import get_config


# --------------------------------------------------------------------------------
# > Models
# --------------------------------------------------------------------------------
class IpAddress(LifeCycleModel):
    """
    List of IP addresses that are either whitelisted or blacklisted
    Only works with IPv4 addresses
    The model is split in the following sections
        Constants
        Fields
        Behavior
        Validators
        Instance Properties
        Instance API
        Request API
        CRON jobs
    """

    # ----------------------------------------
    # Constants
    # ----------------------------------------
    # Static
    COMMENT_MAX_LENGTH = 255

    # Overridable
    DEFAULT_DURATION = 30  # settings.IP_STATUS_DEFAULT_DURATION

    # Statuses
    class IpStatus(IntegerChoices):
        """Possible statuses for an IP Address"""

        NONE = 1
        WHITELISTED = 2
        BLACKLISTED = 3

    # ----------------------------------------
    # Fields
    # ----------------------------------------
    ip = RequiredField(GenericIPAddressField, protocol="IPv4", unique=True)
    status = RequiredField(
        IntegerField, choices=IpStatus.choices, default=IpStatus.NONE
    )
    expires_on = DateField(
        blank=True,
        null=True,
        default=None,
        db_index=True,
        help_text="Expires at the end of said date",
    )
    active = ActiveField()
    comment = CharField(max_length=COMMENT_MAX_LENGTH, blank=True)

    # ----------------------------------------
    # Behavior (meta, str, save)
    # ----------------------------------------
    class Meta:
        """Meta class to setup our database table"""

        db_table = "core_ip_addresses"
        indexes = []
        ordering = ["-id"]
        verbose_name = "IP Address"
        verbose_name_plural = "IP Addresses"

    def __str__(self):
        """
        :return: Returns the IP address
        :rtype: str
        """
        return f"{self.ip}"

    # ----------------------------------------
    # Validators
    # ----------------------------------------
    def clean_comment(self):
        """
        Checks that the comment is not too long
        Specifically useful for sqlite3 who doesn't perform those checks (despite the 'max_length' parameter)
        """
        length = len(self.comment)
        max_length = self.COMMENT_MAX_LENGTH
        if length > max_length:
            raise ValueError(
                f"Value for 'comment' is too long (max: {max_length}, provided: {length})"
            )

    def clean_status(self):
        """Checks that the status is part of the authorized inputs"""
        if self.status not in self.IpStatus.values:
            raise ValueError("Value for 'status' must belong to the 'IpStatus' enum")

    # ----------------------------------------
    # Properties
    # ----------------------------------------
    @property
    def default_duration(self):
        """
        :return: The default duration for a status, which can be overridden in the settings
        :rtype: int
        """
        return get_config("IP_STATUS_DEFAULT_DURATION", self.DEFAULT_DURATION)

    @property
    def is_blacklisted(self):
        """
        :return: Whether the IP is blacklisted
        :rtype: bool
        """
        return (
            self.active
            and (self.expires_on >= date.today())
            and self.status == self.IpStatus.BLACKLISTED
        )

    @property
    def is_whitelisted(self):
        """
        :return: Whether the IP is whitelisted
        :rtype: bool
        """
        return (
            self.active
            and (self.expires_on >= date.today())
            and self.status == self.IpStatus.WHITELISTED
        )

    # ----------------------------------------
    # API for instance
    # ----------------------------------------
    def blacklist(self, end_date=None, comment=None, override=False):
        """
        Blacklists an IP address
        :param Date end_date: The desired expiration date
        :param str comment: The comment to add in the instance
        :param bool override: Whether we allow blacklisting a whitelisted entry
        """
        self._update_status("blacklist", end_date, comment, override)

    def clear(self):
        """Clears an IP address by defaulting its fields to neutral values"""
        self.expires_on = None
        self.active = False
        self.status = self.IpStatus.NONE
        self.save()

    def whitelist(self, end_date=None, comment=None, override=False):
        """
        Whitelists an IP address
        :param Date end_date: The desired expiration date
        :param str comment: The comment to add in the instance
        :param bool override: Whether we allow whitelisting a blacklisted entry
        """
        self._update_status("whitelist", end_date, comment, override)

    def _compute_valid_end_date(self, end_date):
        """
        Defaults the expiration date if none is provided
        :param Date end_date: The desired expiration date
        :return: Either the provided date or the default one
        :rtype: Date
        """
        if end_date is None:
            delta_in_days = timedelta(days=self.default_duration)
            end_date = date.today() + delta_in_days
        return end_date

    def _update_status(self, action, end_date, comment, override):
        """
        Whitelists or blacklists an IP and update all the required fields
        :param str action: Action to perform, used to define the status check
        :param Date end_date: The desired expiration date
        :param str comment: The comment to add in the instance
        :param bool override: Whether we allow whitelisting a blacklisted entry
        """
        if action == "whitelist":
            status_check = self.IpStatus.BLACKLISTED
            new_status = self.IpStatus.WHITELISTED
        else:
            status_check = self.IpStatus.WHITELISTED
            new_status = self.IpStatus.BLACKLISTED
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
        Blacklists an IP address using the provided Request object
        :param Request request: Request object used to get the IP address
        :param Date end_date: The desired expiration date
        :param str comment: The comment to add in the instance
        :param bool override: Whether we allow blacklisting a whitelisted entry
        :return: The updated instance
        :rtype: IpAddress
        """
        instance = cls._fetch_or_add(request)
        instance.blacklist(end_date, comment, override)
        return instance

    @classmethod
    def clear_from_request(cls, request):
        """
        Clears an IP address by defaulting its fields to neutral values
        If IP instance does not exist, does not create it
        :param Request request: Request object used to get the IP address
        :return: The updated instance
        :rtype: IpAddress
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
        Whitelists an IP address using the provided Request object
        :param Request request: Request object used to get the IP address
        :param Date end_date: The desired expiration date
        :param str comment: The comment to add in the instance
        :param bool override: Whether we allow blacklisting a whitelisted entry
        :return: The updated instance
        :rtype: IpAddress
        """
        instance = cls._fetch_or_add(request)
        instance.whitelist(end_date, comment, override)
        return instance

    @classmethod
    def is_blacklisted_from_request(cls, request):
        """
        Checks if an IP address is blacklisted using the Request object
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
        Checks if an IP address is whitelisted using the Request object
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
        Fetches an existing IpAddress instance using the Request object
        :param Request request: A django Request object
        :return: The existing instance linked to this IP
        :rtype: IpAddress
        """
        ip_address = get_client_ip(request)
        instance = get_object_or_none(cls, ip=ip_address)
        return instance

    @classmethod
    def _fetch_or_add(cls, request):
        """
        Fetches an existing IpAddress instance or create a new one using the Request object
        :param Request request: A django Request object
        :return: The found (or newly-added) IpAddress instance
        :rtype: IpAddress
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
        """Clears all IPs whose status has expired"""
        today = date.today()
        ips = cls.objects.filter(expires_on__isnull=False).filter(expires_on__lt=today)
        for ip in ips:
            ip.clear()
