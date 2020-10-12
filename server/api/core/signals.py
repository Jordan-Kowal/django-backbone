"""Signals for the 'core' application"""


# Django
from django.db.models.signals import pre_save
from django.dispatch import receiver

# Local
from .models import IpAddress


# --------------------------------------------------------------------------------
# > Signals
# --------------------------------------------------------------------------------
@receiver(pre_save, sender=IpAddress)
def validate_ip_address_values(sender, instance, **kwargs):
    """
    Check the 'comment' and 'status' fields before saving the instance
    :param Model sender: The model class
    :param Model instance: The model instance
    :param kwargs:
    """
    instance.validate_comment()
    instance.validate_status()
