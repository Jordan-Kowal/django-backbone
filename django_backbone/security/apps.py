"""Config for the 'security' app"""

# Django
from django.apps import AppConfig


# --------------------------------------------------------------------------------
# > Apps
# --------------------------------------------------------------------------------
class SecurityConfig(AppConfig):
    """Base config for the app"""

    name = "security"
    label = "security"

    def ready(self):
        """Imports signals on application start"""
        # Application
        import security.signals
