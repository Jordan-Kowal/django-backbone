"""
Description:
    Contains APIViews and Viewsets for our FAQ API
Serializers:
    ContactViewSet: ViewSet to CREATE new contact entries (user sending us a message)
"""

# Django
from rest_framework import mixins, permissions, viewsets

# Personal
from jklib.django.utils.network import get_client_ip

# Local
from .serializers import ContactSerializer


# --------------------------------------------------------------------------------
# > Serializers
# --------------------------------------------------------------------------------
class ContactViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin):
    """ViewSet to CREATE new contact entries (user sending us a message)"""

    # ----------------------------------------
    # Settings
    # ----------------------------------------
    queryset = None
    serializer_class = ContactSerializer
    permission_classes = (permissions.AllowAny,)

    # ----------------------------------------
    # Actions
    # ----------------------------------------
    def perform_create(self, serializer):
        """Adds the ip field before saving the serializer"""
        serializer.validated_data["ip"] = get_client_ip(self.request)
        instance = serializer.save()
        instance.send_contact_emails(to_admin=True, to_user=True)
