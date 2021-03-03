"""Config for the 'network' app"""

# Django
from django.apps import AppConfig


# --------------------------------------------------------------------------------
# > Apps
# --------------------------------------------------------------------------------
class NetworkConfig(AppConfig):
    """Base config for the app"""

    name = "api.network"
    label = "api.network"

    def ready(self):
        """Imports signals on application start"""
        # Application
        import api.network.signals
