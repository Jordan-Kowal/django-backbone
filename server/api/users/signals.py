"""
Signals for the users API
We use them to:
    User: Create a Profile instance linked to our User on creation
    User: Override the username by the email address on update
    Token: Check the provided data is valid
That way, we can use the email address as username and authentication credentials
"""


# Django
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

# Local
from .models import Profile, Token


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
    """
    if not instance.email:
        raise IntegrityError("User must have a valid email")
    instance.username = instance.email


@receiver(pre_save, sender=Token)
def validate_token_data(sender, instance, **kwargs):
    """Checks that the token type is not too long"""
    instance.validate_type()
