"""
Router management for our API
All the URLs must be defined in this file
"""


# Django
from django.urls import include, path
from rest_framework import routers

# Local
from .contact.viewsets import ContactViewset
from .core.viewsets import NetworkRuleViewSet
from .users.viewsets import AuthViewSet, UserViewSet

# --------------------------------------------------------------------------------
# > URLs
# --------------------------------------------------------------------------------
router = routers.DefaultRouter()
router.register("auth", AuthViewSet, "auth")
router.register("users", UserViewSet, "users")
router.register("network_rules", NetworkRuleViewSet, "network_rules")
router.register("contact", ContactViewset, "contact")
# router.register("example", ClientViewSet, "example")


urlpatterns = [
    path("", include(router.urls)),
]
