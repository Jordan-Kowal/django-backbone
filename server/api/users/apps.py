"""Config for the 'users' app"""

# Django
from django.apps import AppConfig


# --------------------------------------------------------------------------------
# > Apps
# --------------------------------------------------------------------------------
class UsersConfig(AppConfig):
    """Base config for the app"""

    name = "api.users"
    label = "api.users"

    def ready(self):
        """Starts signals at launch"""
        # Application
        import api.users.signals
