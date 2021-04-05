"""Config for the 'core' app"""

# Django
from django.apps import AppConfig


# --------------------------------------------------------------------------------
# > Apps
# --------------------------------------------------------------------------------
class CoreConfig(AppConfig):
    """Base config for the app"""

    name = "core"
    label = "core"

    def ready(self):
        """Starts signals at launch"""
        # Application
        import core.signals
