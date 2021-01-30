"""
Router management for our API
All the URLs must be defined in this file
"""


# Django
from django.urls import include, path
from rest_framework import routers

# Local
from .contact.viewsets import ContactViewset
from .core.viewsets import HealthCheckViewSet, NetworkRuleViewSet
from .users.viewsets import AuthViewSet, UserViewSet

# --------------------------------------------------------------------------------
# > URLs
# --------------------------------------------------------------------------------
router = routers.DefaultRouter()

# Core
router.register("health_checks", HealthCheckViewSet, "health_checks")
router.register("network_rules", NetworkRuleViewSet, "network_rules")

# Contact
router.register("contact", ContactViewset, "contact")

# Users
router.register("auth", AuthViewSet, "auth")
router.register("users", UserViewSet, "users")


urlpatterns = [
    path("", include(router.urls)),
]
