"""IP Addresses"""

# Built-in
from datetime import date, timedelta

# Django
from django.conf import settings
from django.db.models import (
    DateField,
    GenericIPAddressField,
    IntegerChoices,
    IntegerField,
    TextField,
)

# Personal
from jklib.django.db.fields import ActiveField, RequiredField
from jklib.django.db.models import LifeCycleModel
from jklib.django.db.queries import get_object_or_none
from jklib.django.utils.network import get_client_ip


# --------------------------------------------------------------------------------
# > Enums
# --------------------------------------------------------------------------------
class IpStatus(IntegerChoices):
    """Possible statuses for an IP Address"""

    NONE = 1
    WHITELISTED = 2
    BLACKLISTED = 3


# --------------------------------------------------------------------------------
# > Models
# --------------------------------------------------------------------------------
class IpAddress(LifeCycleModel):
    """
    List of IP addresses that are either whitelisted or blacklisted
    Only works with IPv4 addresses

    The API can be used on an instance or the class itself.
    When used as a class method, you must pass the Request object as parameter
        instance.method()               will target the instance
        class.method(request=request)   will find (or create) the instance using the request
    """

    # ----------------------------------------
    # Fields
    # ----------------------------------------
    ip = RequiredField(GenericIPAddressField, protocol="IPv4", unique=True)
    status = IntegerField(choices=IpStatus.choices, default=IpStatus.NONE)
    expires_on = DateField(
        blank=False,
        null=True,
        default=None,
        db_index=True,
        help_text="Expires at the end of said date",
    )
    active = ActiveField()
    comment = TextField(max_length=1000)

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
    # API using Instance or Request
    # ----------------------------------------
    def blacklist(self, end_date=None, comment=None, request=None, override=False):
        """
        Blacklists an IP address
        (If called from the class, the instance will be deduced from the 'request' param)
        :param Date end_date: The desired expiration date
        :param str comment: The comment to add in the instance
        :param Request request: Request object that could be used to get/add the instance
        :param bool override: Whether we allow blacklisting a whitelisted entry
        :return: The updated instance
        :rtype: IpAddress
        """
        instance = self._fetch_or_add(request)
        if comment is not None:
            instance.comment = comment
        instance.expires_on = self._compute_valid_end_date(end_date)
        instance.active = True
        if override or instance.status != IpStatus.WHITELISTED:
            instance.status = IpStatus.BLACKLISTED
        instance.save()
        return instance

    def clear(self, request=None):
        """
        Clears an IP address by defaulting its fields to neutral values
        (If called from the class, the instance will be deduced from the 'request' param)
        :param Request request: Request object that could be used to get/add the instance
        :return: The updated instance
        :rtype: IpAddress
        """
        instance = self._fetch_or_add(request)
        instance.expires_on = None
        instance.active = False
        instance.status = IpStatus.NONE

    def is_blacklisted(self, request=None):
        """
        Checks if an IP address is blacklisted
        (If called from the class, the instance will be deduced from the 'request' param)
        :param Request request: Request object that could be used to get/add the instance
        :return: Whether the IP is blacklisted
        :rtype: bool
        """
        instance = self._fetch_or_add(request)
        return (
            instance.active
            and (instance.expires_on >= date.today())
            and instance.status == IpStatus.BLACKLISTED
        )

    def is_whitelisted(self, request=None):
        """
        Checks if an IP address is whitelisted
        (If called from the class, the instance will be deduced from the 'request' param)
        :param Request request: Request object that could be used to get/add the instance
        :return: Whether the IP is whitelisted
        :rtype: bool
        """
        instance = self._fetch_or_add(request)
        return (
            instance.active
            and (instance.expires_on >= date.today())
            and instance.status == IpStatus.WHITELISTED
        )

    def whitelist(self, end_date=None, comment=None, request=None):
        """
        Whitelists an IP address
        (If called from the class, the instance will be deduced from the 'request' param)
        :param Date end_date: The desired expiration date
        :param str comment: The comment to add in the instance
        :param Request request: Request object that could be used to get/add the instance
        :return: The updated instance
        :rtype: IpAddress
        """
        instance = self._fetch_or_add(request)
        if comment is not None:
            instance.comment = comment
        instance.expires_on = self._compute_valid_end_date(end_date)
        instance.active = True
        instance.status = IpStatus.WHITELISTED
        instance.save()
        return instance

    # ----------------------------------------
    # CRON jobs
    # ----------------------------------------
    @staticmethod
    def clear_expired_entries():
        """Clears all IPs whose status has expired"""
        today = date.today()
        ips = IpAddress.objects.filter(expires_on__isnull=False).filter(
            expires_on__lt=today
        )
        for ip in ips:
            ip.clear()

    # ----------------------------------------
    # Private methods
    # ----------------------------------------
    @staticmethod
    def _compute_valid_end_date(end_date):
        """
        Defaults the expiration date if none is provided
        :param Date end_date: The desired expiration date
        :return: Either the provided date or the default one
        :rtype: Date
        """
        if end_date is None:
            delta_in_days = timedelta(days=settings.IP_STATUS_DEFAULT_DURATION)
            end_date = date.today() + delta_in_days
        return end_date

    def _fetch_or_add(self, request=None):
        """
        Fetches an existing IpAddress instance or create a new one. The logic applied is:
            If performed on an instance, returns the instance
            Else, tries to fetch an existing entry using the Request object
            If none is found, creates a new instance
        :param Request request: A django Request object
        :return: The found (or newly-added) IpAddress instance
        :rtype: IpAddress
        """
        if isinstance(self, (IpAddress,)):
            return self
        ip_address = get_client_ip(request)
        existing_object = get_object_or_none(IpAddress, ip=ip_address)
        if existing_object is not None:
            return existing_object
        else:
            obj = IpAddress(ip=ip_address, active=False)
            return obj
