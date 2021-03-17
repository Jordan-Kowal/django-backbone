"""Signals for the 'security' app"""

# Built-in
import logging

# Django
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

# Local
from .models import NetworkRule

# --------------------------------------------------------------------------------
# > Constants
# --------------------------------------------------------------------------------
LOGGER = logging.getLogger("security")


# --------------------------------------------------------------------------------
# > NetworkRule
# --------------------------------------------------------------------------------
@receiver(post_save, sender=NetworkRule)
def log_rule_update(sender, instance, created, **kwargs):
    """
    Any NetworkRule creation or update will be logged into the system
    :param NetworkRule sender:
    :param NetworkRule instance: The saved instance
    :param bool created: Whether the rule was created
    :param kwargs:
    """
    if created:
        message = f"NetworkRule created for {instance.ip} (Status: {instance.computed_status})"
    else:
        message = f"NetworkRule updated for {instance.ip} (Status: {instance.computed_status})"
    LOGGER.info(message)


@receiver(post_delete, sender=NetworkRule)
def log_rule_deletion(sender, instance, **kwargs):
    """
    Any NetworkRule deletion will be logged into the system
    :param NetworkRule sender:
    :param NetworkRule instance: The deleted instance
    :param kwargs:
    """
    LOGGER.info(
        f"NetworkRule deleted for {instance.ip} (Status: {instance.computed_status})"
    )
