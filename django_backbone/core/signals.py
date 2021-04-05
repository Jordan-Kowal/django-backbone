"""Signals for the 'core' app"""

# Django
from django.contrib.auth import get_user_model
from django.contrib.sessions.models import Session
from django.db.models.signals import pre_save
from django.dispatch import receiver


# --------------------------------------------------------------------------------
# > Shared
# --------------------------------------------------------------------------------
@receiver(pre_save)
def automatic_pre_save_full_clean(sender, instance, **kwargs):
    """
    Runs the `full_clean` method before saving the instance, unless this model is exempted
    :param Model sender: The model class
    :param Model instance: The model instance
    :param kwargs:
    """
    whitelist = {Session, get_user_model()}
    if sender not in whitelist:
        instance.full_clean()
