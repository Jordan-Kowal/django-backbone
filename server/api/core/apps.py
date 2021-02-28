"""Config for the 'core' app"""

# Django
from django.apps import AppConfig


# --------------------------------------------------------------------------------
# > Apps
# --------------------------------------------------------------------------------
class CoreConfig(AppConfig):
    """Base config for the app"""

    name = "api.core"
    label = "api.core"

    def ready(self):
        """Starts signals at launch"""
        # Application
        import api.core.signals
