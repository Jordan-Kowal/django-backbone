"""Signals for the 'core' application"""


# Django
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from django.db.models.signals import pre_save
from django.dispatch import receiver


# --------------------------------------------------------------------------------
# > Signals
# --------------------------------------------------------------------------------
@receiver(pre_save)
def automatic_pre_save_full_clean(sender, instance, **kwargs):
    """
    Runs the `full_clean` method before saving the instance, unless this model is exempted
    :param Model sender: The model class
    :param Model instance: The model instance
    :param kwargs:
    """
    whitelist = {Session, User}
    if sender not in whitelist:
        instance.full_clean()
