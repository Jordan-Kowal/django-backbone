"""Viewsets for the 'security' app"""

# Django
from django.db.models import Q
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
    HTTP_409_CONFLICT,
)

# Personal
from jklib.django.drf.permissions import IsAdminUser
from jklib.django.drf.serializers import IdListSerializer
from jklib.django.drf.viewsets import ImprovedModelViewSet

# Local
from .models import NetworkRule
from .serializers import (
    ActivateNetworkRuleSerializer,
    ActivateNewNetworkRuleSerializer,
    NetworkRuleSerializer,
    StatusSerializer,
)


# --------------------------------------------------------------------------------
# > ViewSets
# --------------------------------------------------------------------------------
class NetworkRuleViewSet(ImprovedModelViewSet):
    """Viewset for the NetworkRule model"""

    queryset = NetworkRule.objects.all()
    viewset_permission_classes = (IsAdminUser,)
    serializer_classes = {
        "default": NetworkRuleSerializer,
        "activate_existing": ActivateNetworkRuleSerializer,
        "activate_new": ActivateNewNetworkRuleSerializer,
        "bulk_destroy": IdListSerializer,
        "bulk_clear": StatusSerializer,
    }

    @action(detail=True, methods=["put"], url_path="activate")
    def activate_existing(self, request, pk=None):
        """Blacklists or whitelists an existing rule. Can return 409 if conflict without override"""
        instance = self.get_object()
        serializer = self.get_valid_serializer(instance, data=request.data)
        payload = {
            "end_date": serializer.validated_data.get("expires_on", None),
            "comment": serializer.validated_data.get("comment", None),
            "override": serializer.validated_data.get("override", False),
        }
        status = serializer.validated_data["status"]
        if status == NetworkRule.Status.WHITELISTED:
            if instance.is_blacklisted and not payload["override"]:
                return Response(None, status=HTTP_409_CONFLICT)
            instance.whitelist(**payload)
        else:
            if instance.is_whitelisted and not payload["override"]:
                return Response(None, status=HTTP_409_CONFLICT)
            instance.blacklist(**payload)
        serializer = self.get_serializer(instance)
        serializer.data.pop("override", None)
        return Response(serializer.data, status=HTTP_200_OK)

    @action(detail=False, methods=["post"], url_path="activate")
    def activate_new(self, request):
        """Creates a new blacklist or whitelist rule"""
        serializer = self.get_valid_serializer(data=request.data)
        instance = serializer.save()
        payload = {
            "end_date": serializer.validated_data.get("expires_on", None),
            "comment": serializer.validated_data.get("comment", None),
            "override": True,
        }
        status = serializer.validated_data["status"]
        if status == NetworkRule.Status.WHITELISTED:
            instance.whitelist(**payload)
        else:
            instance.blacklist(**payload)
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=HTTP_201_CREATED)

    @action(detail=False, methods=["post"], url_path="clear")
    def bulk_clear(self, request):
        """Clears multiple rules at once"""
        serializer = self.get_valid_serializer(data=request.data)
        status = serializer.validated_data.get("status", None)
        # Build the query
        if status is None:
            query = (
                Q(active=True)
                | ~Q(expires_on=None)
                | ~Q(status=NetworkRule.Status.NONE)
            )
        else:
            query = Q(status=status)
        eligible_instances = NetworkRule.objects.filter(query)
        # Apply changes
        for instance in eligible_instances:
            instance.clear()
        return Response(None, status=HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["put"])
    def clear(self, request, pk=None):
        """Clears an existing rule"""
        instance = self.get_object()
        instance.clear()
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=HTTP_200_OK)
