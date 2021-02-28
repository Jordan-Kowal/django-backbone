"""Signals for the 'users' app"""


# Django
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

# Local
from .models import Profile


# --------------------------------------------------------------------------------
# > Signals
# --------------------------------------------------------------------------------
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Creates a Profile instance whenever a User is created"""
    if created:
        Profile.objects.create(user=instance)


@receiver(pre_save, sender=User)
def username_is_email(sender, instance, **kwargs):
    """
    Overrides the username with the email before saving
    The email address cannot be empty
    :raises IntegrityError: When the user does not have an email address
    """
    if not instance.email:
        raise IntegrityError("User must have a valid email")
    instance.username = instance.email
