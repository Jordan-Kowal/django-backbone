"""Viewsets for the 'contact' app"""

# Built-in
from datetime import date, timedelta

# Django
from rest_framework.mixins import (
    CreateModelMixin,
    DestroyModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
)
from rest_framework.response import Response
from rest_framework.status import HTTP_204_NO_CONTENT, HTTP_403_FORBIDDEN

# Personal
from jklib.django.drf.permissions import AllowAny, IsAdminUser
from jklib.django.drf.serializers import IdListSerializer
from jklib.django.drf.viewsets import BulkDestroyMixin, ImprovedViewSet
from jklib.django.utils.network import get_client_ip

# Application
from security.models import NetworkRule

# Local
from .models import Contact
from .serializers import ApiCreateContactSerializer, ContactSerializer


# --------------------------------------------------------------------------------
# > ViewSets
# --------------------------------------------------------------------------------
class ContactViewset(
    BulkDestroyMixin,
    CreateModelMixin,
    RetrieveModelMixin,
    ListModelMixin,
    DestroyModelMixin,
    ImprovedViewSet,
):
    """ViewSet for the Contact model"""

    queryset = Contact.objects.all()
    viewset_permissions = None
    permission_classes = {
        "default": (IsAdminUser,),
        "create": (AllowAny,),
    }
    serializer_classes = {
        "default": ContactSerializer,
        "create": ApiCreateContactSerializer,
        "bulk_destroy": IdListSerializer,
    }

    def create(self, request, *args, **kwargs):
        """Creates a Contact instance, sends emails, and maybe blacklists the user"""
        serializer = self.get_valid_serializer(data=request.data)
        notify_user = serializer.validated_data.pop("notify_user")
        ip = get_client_ip(self.request)
        user = None if request.user.is_anonymous else request.user
        # Maybe refuse and ban
        if Contact.should_ban_ip(ip=ip):
            ban_settings = Contact.get_ban_settings()
            ban_end_date = date.today() + timedelta(
                days=ban_settings["duration_in_days"]
            )
            NetworkRule.blacklist_from_request(
                request=self.request,
                end_date=ban_end_date,
                comment="Too many requests in the Contact API",
            )
            return Response(None, status=HTTP_403_FORBIDDEN)
        # Accept the contact
        else:
            contact = serializer.save(ip=ip, user=user)
            contact.send_notifications(True, notify_user)
            return Response(None, status=HTTP_204_NO_CONTENT)
