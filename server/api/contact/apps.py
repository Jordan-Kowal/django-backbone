"""Config for the 'contact' app"""


# Django
from django.apps import AppConfig


# --------------------------------------------------------------------------------
# > Apps
# --------------------------------------------------------------------------------
class ContactConfig(AppConfig):
    """Base config for the app"""

    name = "api.contact"
    label = "api.contact"
