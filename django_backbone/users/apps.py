"""Config for the 'users' app"""

# Django
from django.apps import AppConfig


# --------------------------------------------------------------------------------
# > Apps
# --------------------------------------------------------------------------------
class UsersConfig(AppConfig):
    """Base config for the app"""

    name = "users"
    label = "users"
