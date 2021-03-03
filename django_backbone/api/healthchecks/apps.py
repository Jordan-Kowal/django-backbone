"""Config for the 'healthchecks' app"""

# Django
from django.apps import AppConfig


# --------------------------------------------------------------------------------
# > Apps
# --------------------------------------------------------------------------------
class HealthchecksConfig(AppConfig):
    """Base config for the app"""

    name = "api.healthchecks"
    label = "api.healthchecks"
