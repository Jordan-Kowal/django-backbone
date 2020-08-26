"""
Contains the signals for the users API
1) User & Profile
    To customize the User model without overriding it, we create the Profile model
    A signal is used to automatically create a Profile when a User is created
2) Username and Email
    To use the "email" as the username, without overriding the auth process
    We simply made sure that the username always has the same value as the email
    Also, our "serializer" makes sure the email is unique
Signals:
    extend_user: Extends our user by creating its associated model instances
    username_is_email: Before saving a user, we override the username with the email
"""


# Django
from django.contrib.auth.models import User
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

# Local
from .models import Profile


# --------------------------------------------------------------------------------
# > Signals
# --------------------------------------------------------------------------------
@receiver(post_save, sender=User)
def extend_user(sender, instance, created, **kwargs):
    """Automatically creates a Profile instance whenever a User is created"""
    if created:
        Profile.objects.create(user=instance)


@receiver(pre_save, sender=User)
def username_is_email(sender, instance, **kwargs):
    """Before saving a user, we override the username with the email"""
    instance.username = instance.email
