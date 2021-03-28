"""
Router management for our API
All the URLs must be defined in this file
"""


# Django
from django.urls import include, path

# Personal
from jklib.django.drf.routers import ImprovedRouter

# Local
from .contact.viewsets import ContactViewset
from .healthchecks.viewsets import HealthcheckViewSet
from .security.viewsets import NetworkRuleViewSet
from .users.viewsets import AuthViewSet, UserViewSet

# --------------------------------------------------------------------------------
# > URLs
# --------------------------------------------------------------------------------
router = ImprovedRouter()

router.register("auth", AuthViewSet, "auth")
router.register("contacts", ContactViewset, "contacts")
router.register("healthchecks", HealthcheckViewSet, "healthchecks")
router.register("network_rules", NetworkRuleViewSet, "network_rules")
router.register("users", UserViewSet, "users")

urlpatterns = [
    path("", include(router.urls)),
]
