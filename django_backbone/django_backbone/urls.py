"""
Our project URL Configuration
The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""


# Django
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path

# Personal
from jklib.django.drf.routers import ImprovedRouter

# Application
from contact.viewsets import ContactViewset
from healthchecks.viewsets import HealthcheckViewSet
from security.viewsets import NetworkRuleViewSet
from users.viewsets import UserAdminViewSet, UserViewSet

# --------------------------------------------------------------------------------
# > URLs
# --------------------------------------------------------------------------------
router = ImprovedRouter()
router.register("admin/healthchecks", HealthcheckViewSet, "admin_healthchecks")
router.register("admin/network_rules", NetworkRuleViewSet, "admin_network_rules")
router.register("admin/users", UserAdminViewSet, "admin_users")
# router.register("auth", AuthViewSet, "auth")
router.register("contacts", ContactViewset, "contacts")
router.register("users", UserViewSet, "users")

urlpatterns = [
    path("api/", include(router.urls), name="api"),
]

# Media
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
